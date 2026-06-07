"""Automation task runner with permission checks and event updates."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.automation.plugin_base import SanayaPlugin
from core.db.models import Task
from core.event_bus import EventBus
from core.security.permission_engine import PermissionEngine


class TaskRunner:
    """Runs automation plugins and persists task lifecycle state."""

    def __init__(self, db: AsyncSession, event_bus: EventBus) -> None:
        """Bind database, events, and permission engine."""
        self.db = db
        self.event_bus = event_bus
        self.permissions = PermissionEngine(db)

    async def run(self, plugin: SanayaPlugin, command: str, params: dict[str, Any], context: dict[str, Any]) -> str:
        """Run a plugin after verifying all required permissions."""
        for permission in plugin.manifest.permissions:
            await self.permissions.require_permission(plugin.manifest.name, permission)
        task = Task(name=command, plugin=plugin.manifest.name, params=params, status="running", started_at=datetime.utcnow())
        self.db.add(task)
        await self.db.commit()
        await self.event_bus.publish("automation.task.started", {"task_id": task.id, "plugin": plugin.manifest.name})
        try:
            task.result = await plugin.execute(command, params, context)
            task.status = "done"
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)
        task.finished_at = datetime.utcnow()
        await self.db.commit()
        await self.event_bus.publish("automation.task.complete", {"task_id": task.id, "status": task.status, "result": task.result, "error": task.error})
        return task.id
