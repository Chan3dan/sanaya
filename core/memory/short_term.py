"""Redis-backed short-term session memory."""

import json
from typing import Any

import redis.asyncio as redis

from core.config import config


class ShortTermMemory:
    """Stores recent conversation turns with a TTL."""

    def __init__(self) -> None:
        """Create Redis client."""
        self.client = redis.from_url(config.redis_url, decode_responses=True)

    def _key(self, session_id: str) -> str:
        """Return the Redis key for a session."""
        return f"stm:session:{session_id}"

    async def store(self, session_id: str, messages: list[dict[str, Any]], ttl: int = 7200) -> None:
        """Store all messages for a session."""
        await self.client.set(self._key(session_id), json.dumps(messages), ex=ttl)

    async def get(self, session_id: str) -> list[dict[str, Any]]:
        """Return recent messages for a session."""
        raw = await self.client.get(self._key(session_id))
        return json.loads(raw) if raw else []

    async def append(self, session_id: str, message: dict[str, Any]) -> None:
        """Append one message to a session."""
        messages = await self.get(session_id)
        messages.append(message)
        await self.store(session_id, messages)

    async def clear(self, session_id: str) -> None:
        """Clear session memory."""
        await self.client.delete(self._key(session_id))
