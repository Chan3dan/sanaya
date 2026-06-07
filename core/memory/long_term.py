"""Encrypted SQL long-term memory."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import Memory
from core.security.key_manager import KeyManager


class LongTermMemory:
    """Stores encrypted durable memories."""

    def __init__(self, db: AsyncSession, key_manager: KeyManager) -> None:
        """Bind database and key manager."""
        self.db = db
        self.key_manager = key_manager

    async def store(self, content: str, type: str, importance: float, tags: list[str], is_private: bool) -> Memory:
        """Store an encrypted memory."""
        memory = Memory(
            type=type,
            content=self.key_manager.encrypt_text(content),
            summary=content[:240],
            importance=importance,
            tags=tags,
            is_private=is_private,
        )
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def get(self, memory_id: str) -> Memory | None:
        """Get and decrypt a memory by ID."""
        memory = await self.db.get(Memory, memory_id)
        if memory:
            memory.content = self.key_manager.decrypt_text(memory.content)
        return memory

    async def search(self, query: str, limit: int = 10, type_filter: str | None = None) -> list[Memory]:
        """Search memories by summary text."""
        stmt = select(Memory).where(Memory.summary.contains(query)).limit(limit)
        if type_filter:
            stmt = stmt.where(Memory.type == type_filter)
        rows = list(await self.db.scalars(stmt))
        for row in rows:
            row.content = self.key_manager.decrypt_text(row.content)
        return rows

    async def update_access(self, memory_id: str) -> None:
        """Increment access counters."""
        memory = await self.db.get(Memory, memory_id)
        if memory:
            memory.access_count += 1
            await self.db.commit()

    async def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        memory = await self.db.get(Memory, memory_id)
        if memory:
            await self.db.delete(memory)
            await self.db.commit()
