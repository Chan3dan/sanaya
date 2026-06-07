"""Sanaya core orchestrator and FastAPI health server."""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import delete, desc, select

from core.ai.base_provider import Message
from core.ai.router import AIRouter
from core.automation.plugin_registry import PluginRegistry
from core.automation.task_runner import TaskRunner
from core.config import config
from core.db.models import Conversation, Memory, PluginPermission, Task
from core.db.session import create_all_tables, engine
from core.db.session import SessionLocal
from core.event_bus import EventBus
from core.memory.manager import MemoryManager
from core.memory.long_term import LongTermMemory
from core.security.key_manager import KeyManager

app = FastAPI(title="Sanaya Core", version="1.0.0")
bus: EventBus | None = None
registry: PluginRegistry | None = None
ai_router = AIRouter()


class ChatRequest(BaseModel):
    """Manual chat request."""

    text: str = Field(min_length=1)
    session_id: str = "default"


class MemoryRequest(BaseModel):
    """Memory create request."""

    content: str = Field(min_length=1)
    type: str = "fact"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = []
    is_private: bool = False
    source: str = "manual"


class AutomationRequest(BaseModel):
    """Automation command request."""

    command: str = Field(min_length=1)
    params: dict[str, Any] = {}
    session_id: str = "default"


def serialize_memory(memory: Memory) -> dict[str, Any]:
    """Return API-safe memory fields."""
    return {
        "id": memory.id,
        "type": memory.type,
        "content": memory.content,
        "summary": memory.summary,
        "importance": memory.importance,
        "is_private": memory.is_private,
        "source": memory.source,
        "tags": memory.tags,
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
        "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
    }


def serialize_task(task: Task) -> dict[str, Any]:
    """Return API-safe task fields."""
    return {
        "id": task.id,
        "name": task.name,
        "plugin": task.plugin,
        "status": task.status,
        "params": task.params,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    }


@app.get("/health")
async def health() -> dict:
    """Return core process health."""
    return {
        "status": "ok",
        "service": "sanaya-core",
        "wake_word_model": Path(config.wake_word_model).exists(),
        "wake_word_mode": "model" if Path(config.wake_word_model).exists() else "manual",
        "ollama_model": config.ollama_chat_model,
    }


@app.get("/chat/history")
async def chat_history(session_id: str = "default", limit: int = Query(default=50, ge=1, le=200)) -> list[dict[str, Any]]:
    """Return persisted conversation history."""
    async with SessionLocal() as session:
        rows = list(
            await session.scalars(
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(desc(Conversation.timestamp))
                .limit(limit)
            )
        )
    return [
        {
            "id": row.id,
            "role": row.role,
            "content": row.content,
            "provider": row.provider_used,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        }
        for row in reversed(rows)
    ]


@app.post("/chat/message")
async def chat_message(request: ChatRequest) -> dict[str, Any]:
    """Persist a user message, generate a local response, and persist the reply."""
    started = time.perf_counter()
    text = request.text.strip()
    async with SessionLocal() as session:
        user_turn = Conversation(session_id=request.session_id, role="user", content=text)
        session.add(user_turn)
        await session.commit()

        tokens: list[str] = []
        async for token in ai_router.stream_chat([Message("user", text)], privacy_required=True):
            tokens.append(token)
        content = "".join(tokens).strip() or "Sanaya did not return a response."
        latency_ms = int((time.perf_counter() - started) * 1000)
        assistant_turn = Conversation(
            session_id=request.session_id,
            role="assistant",
            content=content,
            provider_used="ollama",
            latency_ms=latency_ms,
        )
        session.add(assistant_turn)
        await session.commit()
        await session.refresh(assistant_turn)

    if bus is not None:
        await bus.publish("ai.response.done", {"message_id": assistant_turn.id, "provider": "ollama", "model": config.ollama_chat_model, "content": content})
    return {"message_id": assistant_turn.id, "provider": "ollama", "model": config.ollama_chat_model, "content": content, "latency_ms": latency_ms}


@app.delete("/chat/history")
async def clear_chat_history(session_id: str = "default") -> dict[str, Any]:
    """Delete persisted conversation history for a session."""
    async with SessionLocal() as session:
        result = await session.execute(delete(Conversation).where(Conversation.session_id == session_id))
        await session.commit()
    return {"deleted": result.rowcount or 0}


@app.get("/memory")
async def list_memory(type: str | None = None, limit: int = Query(default=50, ge=1, le=200)) -> list[dict[str, Any]]:
    """List durable memories."""
    async with SessionLocal() as session:
        store = LongTermMemory(session, KeyManager())
        rows = await store.search("", limit=limit, type_filter=type)
    return [serialize_memory(row) for row in rows]


@app.post("/memory")
async def create_memory(request: MemoryRequest) -> dict[str, Any]:
    """Create a durable memory."""
    async with SessionLocal() as session:
        key_manager = KeyManager()
        memory = Memory(
            type=request.type,
            content=key_manager.encrypt_text(request.content),
            summary=request.content[:240],
            importance=request.importance,
            tags=request.tags,
            is_private=request.is_private,
            source=request.source,
        )
        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        memory.content = request.content
    if bus is not None:
        await bus.publish("memory.stored", {"memory_id": memory.id, "summary": memory.summary})
    return serialize_memory(memory)


@app.get("/memory/search")
async def search_memory(q: str = "", type: str | None = None, limit: int = Query(default=10, ge=1, le=50)) -> list[dict[str, Any]]:
    """Search durable memories by text."""
    async with SessionLocal() as session:
        store = LongTermMemory(session, KeyManager())
        rows = await store.search(q, limit=limit, type_filter=type)
    return [serialize_memory(row) for row in rows]


@app.patch("/memory/{memory_id}")
async def update_memory(memory_id: str, request: MemoryRequest) -> dict[str, Any]:
    """Update a durable memory."""
    async with SessionLocal() as session:
        memory = await session.get(Memory, memory_id)
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found.")
        key_manager = KeyManager()
        memory.content = key_manager.encrypt_text(request.content)
        memory.summary = request.content[:240]
        memory.type = request.type
        memory.importance = request.importance
        memory.tags = request.tags
        memory.is_private = request.is_private
        memory.source = request.source
        memory.updated_at = datetime.utcnow()
        await session.commit()
        memory.content = request.content
    return serialize_memory(memory)


@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str) -> dict[str, Any]:
    """Delete a durable memory."""
    async with SessionLocal() as session:
        memory = await session.get(Memory, memory_id)
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found.")
        await session.delete(memory)
        await session.commit()
    return {"deleted": True, "id": memory_id}


@app.get("/automation/plugins")
async def list_plugins() -> list[dict[str, Any]]:
    """List discovered automation plugins."""
    if registry is None:
        raise HTTPException(status_code=503, detail="Automation registry is not ready.")
    return [
        {
            "name": plugin.manifest.name,
            "description": plugin.manifest.description,
            "triggers": plugin.manifest.triggers,
            "permissions": plugin.manifest.permissions,
            "supports_undo": plugin.manifest.supports_undo,
        }
        for plugin in registry.plugins
    ]


@app.post("/automation/run")
async def run_automation(request: AutomationRequest) -> dict[str, Any]:
    """Run the best matching automation plugin for a command."""
    if registry is None:
        raise HTTPException(status_code=503, detail="Automation registry is not ready.")
    plugin = registry.find_plugin(request.command)
    if plugin is None:
        raise HTTPException(status_code=404, detail="No automation plugin matched the command.")
    async with SessionLocal() as session:
        runner = TaskRunner(session, bus or EventBus())
        task_id = await runner.run(plugin, request.command, request.params, {"session_id": request.session_id})
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=500, detail="Task disappeared after execution.")
        return serialize_task(task)


@app.post("/voice/manual")
async def manual_voice_command(request: AutomationRequest) -> dict[str, Any]:
    """Handle a typed command as the Phase 1 manual wake-word fallback."""
    command = request.command.strip()
    lowered = command.lower()
    for prefix in ("hey sanaya,", "hey sanaya"):
        if lowered.startswith(prefix):
            command = command[len(prefix):].strip()
            break
    return await run_automation(AutomationRequest(command=command, params=request.params, session_id=request.session_id))


async def validate_startup() -> list[str]:
    """Validate critical local services and paths."""
    errors: list[str] = []
    try:
        client = redis.from_url(config.redis_url)
        await client.ping()
    except Exception as exc:
        errors.append(f"Redis is not reachable at {config.redis_url}: {exc}")
    if not Path(config.wake_word_model).exists():
        logger.warning("Wake word model missing at {}; starting with manual activation fallback.", config.wake_word_model)
    return errors


async def startup_sequence() -> EventBus:
    """Initialize database, event bus, memory, and automation."""
    global bus, registry
    Path("./data/sqlite").mkdir(parents=True, exist_ok=True)
    Path(config.chroma_path).mkdir(parents=True, exist_ok=True)
    await create_all_tables()
    bus = EventBus()
    registry = PluginRegistry()
    registry.discover()
    async with SessionLocal() as session:
        for plugin in registry.plugins:
            for permission in plugin.manifest.permissions:
                existing = await session.get(PluginPermission, {"plugin_name": plugin.manifest.name, "permission": permission})
                if existing is None:
                    session.add(PluginPermission(plugin_name=plugin.manifest.name, permission=permission, granted=True, granted_at=datetime.utcnow()))
        await session.commit()
    memory = MemoryManager(bus)
    await memory.start()
    await bus.publish("system.startup.complete", {"status": "ready"})
    logger.info("Sanaya startup complete")
    return bus


async def main() -> None:
    """Run startup validation and serve the core API."""
    errors = await validate_startup()
    if errors:
        for error in errors:
            logger.error(error)
        raise SystemExit(1)
    await startup_sequence()
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=config.sanaya_core_port, log_level="info"))
    await server.serve()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
