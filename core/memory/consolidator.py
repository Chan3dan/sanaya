"""Scheduled consolidation of short-term memories into long-term facts."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class MemoryConsolidator:
    """Runs scheduled memory consolidation jobs."""

    def __init__(self) -> None:
        """Create scheduler."""
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        """Start daily consolidation schedule."""
        self.scheduler.add_job(self.consolidate, "cron", hour=3, minute=0)
        self.scheduler.start()

    async def consolidate(self) -> None:
        """Extract durable facts from yesterday's sessions."""
        return None
