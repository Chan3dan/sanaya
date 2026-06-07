"""Redis Pub/Sub event bus for module-only communication."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import redis.asyncio as redis
from loguru import logger

from core.config import config

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    """Thin Redis Pub/Sub wrapper with JSON payloads and reconnection."""

    def __init__(self, redis_url: str = config.redis_url) -> None:
        """Create an event bus for the configured Redis URL."""
        self.redis_url = redis_url
        self.client = redis.from_url(redis_url, decode_responses=True)

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """Publish a JSON event payload."""
        try:
            await self.client.publish(channel, json.dumps(payload))
            logger.bind(channel=channel).info("event.published")
        except redis.ConnectionError:
            logger.warning("Redis publish failed; reconnecting")
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.publish(channel, json.dumps(payload))

    async def subscribe(self, channel: str, handler: EventHandler) -> None:
        """Subscribe to a channel forever and dispatch events to a handler."""
        while True:
            try:
                pubsub = self.client.pubsub()
                await pubsub.subscribe(channel)
                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue
                    payload = json.loads(message["data"])
                    logger.bind(channel=channel).info("event.received")
                    await handler(payload)
            except (redis.ConnectionError, json.JSONDecodeError) as exc:
                logger.warning(f"Event subscription interrupted: {exc}")
                await asyncio.sleep(1)
