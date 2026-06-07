"""Async database engine, sessions, and startup seed data."""

from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import config
from core.db.models import Base, Preference

engine = create_async_engine(config.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def _ensure_sqlite_parent() -> None:
    """Create the parent folder for local SQLite database URLs."""
    parsed = urlparse(config.database_url)
    if parsed.scheme not in {"sqlite", "sqlite+aiosqlite"}:
        return
    database_path = parsed.path.lstrip("/")
    if database_path:
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional async database session."""
    async with SessionLocal() as session:
        async with session.begin():
            yield session


async def create_all_tables() -> None:
    """Create all database tables and seed default preferences."""
    _ensure_sqlite_parent()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        defaults = {
            "ai.default_provider": ("ollama", "ai"),
            "ai.privacy_mode": (False, "privacy"),
            "voice.tts_provider": ("coqui", "voice"),
            "voice.wake_sensitivity": (0.5, "voice"),
            "automation.confirm": (True, "automation"),
        }
        for key, (value, category) in defaults.items():
            exists = await session.scalar(select(Preference).where(Preference.key == key))
            if exists is None:
                session.add(Preference(key=key, value=value, category=category))
        await session.commit()
