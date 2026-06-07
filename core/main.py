"""Sanaya core orchestrator and FastAPI health server."""

import asyncio
from pathlib import Path

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from loguru import logger

from core.automation.plugin_registry import PluginRegistry
from core.config import config
from core.db.session import create_all_tables, engine
from core.event_bus import EventBus
from core.memory.manager import MemoryManager

app = FastAPI(title="Sanaya Core", version="1.0.0")


@app.get("/health")
async def health() -> dict:
    """Return core process health."""
    return {"status": "ok", "service": "sanaya-core"}


async def validate_startup() -> list[str]:
    """Validate critical local services and paths."""
    errors: list[str] = []
    try:
        client = redis.from_url(config.redis_url)
        await client.ping()
    except Exception as exc:
        errors.append(f"Redis is not reachable at {config.redis_url}: {exc}")
    if not Path(config.wake_word_model).exists():
        errors.append(f"Wake word model missing at {config.wake_word_model}. Run scripts/download_models.py.")
    return errors


async def startup_sequence() -> EventBus:
    """Initialize database, event bus, memory, and automation."""
    Path("./data/sqlite").mkdir(parents=True, exist_ok=True)
    Path(config.chroma_path).mkdir(parents=True, exist_ok=True)
    await create_all_tables()
    bus = EventBus()
    registry = PluginRegistry()
    registry.discover()
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
