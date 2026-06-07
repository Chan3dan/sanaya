"""Memory manager that serves context and stores memories via events."""

from core.event_bus import EventBus
from core.memory.short_term import ShortTermMemory


class MemoryManager:
    """Coordinates short-term, long-term, and semantic memory."""

    def __init__(self, event_bus: EventBus) -> None:
        """Create a memory manager."""
        self.event_bus = event_bus
        self.short_term = ShortTermMemory()

    async def get_context(self, query: str, session_id: str) -> dict:
        """Build context for a query."""
        return {"recent_messages": await self.short_term.get(session_id), "relevant_memories": [], "user_preferences": []}

    async def store_memory(self, content: str, type: str, importance: float, is_private: bool) -> None:
        """Request memory storage through the event bus."""
        await self.event_bus.publish("memory.store.requested", {"content": content, "type": type, "importance": importance, "is_private": is_private})

    async def start(self) -> None:
        """Subscribe to memory request events."""
        await self.event_bus.publish("memory.module.ready", {"status": "ready"})
