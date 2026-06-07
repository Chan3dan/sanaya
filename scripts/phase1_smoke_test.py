"""End-to-end Phase 1 smoke tests for local Sanaya services."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any
from urllib import request

import redis.asyncio as redis

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import config


API_URL = "http://127.0.0.1:3001/api/v1"
CORE_URL = "http://127.0.0.1:8000"
OLLAMA_URL = "http://127.0.0.1:11434"
DASHBOARD_URL = "http://127.0.0.1:3000"


def http_json(method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
    """Send a JSON request and return parsed JSON."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=data, method=method, headers={"content-type": "application/json"})
    with request.urlopen(req, timeout=120) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else None


def http_status(url: str) -> int:
    """Return HTTP status for a URL."""
    with request.urlopen(url, timeout=15) as response:
        return response.status


async def redis_ping() -> bool:
    """Return whether Redis responds."""
    client = redis.from_url(config.redis_url)
    try:
        return bool(await client.ping())
    finally:
        await client.aclose()


def assert_true(name: str, condition: bool) -> None:
    """Print and enforce one smoke-test assertion."""
    print(f"{'PASS' if condition else 'FAIL'} {name}")
    if not condition:
        raise AssertionError(name)


async def main() -> int:
    """Run all Phase 1 smoke checks."""
    try:
        assert_true("dashboard loads", http_status(DASHBOARD_URL) == 200)
        assert_true("api health", http_json("GET", f"{API_URL}/health")["status"] == "ok")
        core_health = http_json("GET", f"{CORE_URL}/health")
        assert_true("core health", core_health["status"] == "ok")
        assert_true("manual wake fallback or wake model available", core_health["wake_word_mode"] in {"manual", "model"})
        assert_true("redis ping", await redis_ping())
        models = http_json("GET", f"{OLLAMA_URL}/api/tags")["models"]
        assert_true("ollama chat model installed", any(model["name"] == config.ollama_chat_model for model in models))

        chat = http_json("POST", f"{API_URL}/chat/message", {"text": "Say: phase one smoke chat", "session_id": "phase1-smoke"})
        assert_true("chat returns assistant content", bool(chat.get("content")))
        history = http_json("GET", f"{API_URL}/chat/history?session_id=phase1-smoke")
        assert_true("chat history persisted", len(history) >= 2 and history[-1]["role"] == "assistant")

        memory = http_json("POST", f"{API_URL}/memory", {"content": "Phase one smoke memory", "type": "fact", "source": "smoke"})
        assert_true("memory create returns readable content", memory["content"] == "Phase one smoke memory")
        search = http_json("GET", f"{API_URL}/memory/search?q=smoke")
        assert_true("memory search finds created item", any(item["id"] == memory["id"] for item in search))
        deleted = http_json("DELETE", f"{API_URL}/memory/{memory['id']}")
        assert_true("memory delete works", deleted["deleted"] is True)

        plugins = http_json("GET", f"{API_URL}/automation/plugins")
        assert_true("automation plugins loaded", len(plugins) >= 4)
        task = http_json("POST", f"{API_URL}/automation/voice/manual", {"command": "Hey Sanaya, find .", "params": {"action": "list", "path": "."}})
        assert_true("manual wake automation works", task["status"] == "done" and task["result"]["success"] is True)
    except Exception as exc:
        print(f"Phase 1 smoke test failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
