"""Permission checks for automation plugins."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import PluginPermission


class PermissionDeniedError(RuntimeError):
    """Raised when a plugin does not have a required permission."""


class PermissionEngine:
    """Stores and evaluates plugin permissions."""

    def __init__(self, db: AsyncSession) -> None:
        """Bind the engine to a database session."""
        self.db = db

    async def check_permission(self, plugin_name: str, permission: str) -> bool:
        """Return whether a plugin permission is granted."""
        row = await self.db.scalar(
            select(PluginPermission).where(
                PluginPermission.plugin_name == plugin_name,
                PluginPermission.permission == permission,
            )
        )
        return bool(row and row.granted)

    async def require_permission(self, plugin_name: str, permission: str) -> None:
        """Raise if a plugin permission is not granted."""
        if not await self.check_permission(plugin_name, permission):
            raise PermissionDeniedError(f"Permission denied: {plugin_name} requires {permission}")

    async def grant_permission(self, plugin_name: str, permission: str) -> None:
        """Grant a plugin permission."""
        row = await self.db.get(PluginPermission, {"plugin_name": plugin_name, "permission": permission})
        if row:
            row.granted = True
            row.granted_at = datetime.utcnow()
        else:
            self.db.add(PluginPermission(plugin_name=plugin_name, permission=permission, granted=True, granted_at=datetime.utcnow()))
        await self.db.commit()

    async def revoke_permission(self, plugin_name: str, permission: str) -> None:
        """Revoke a plugin permission."""
        row = await self.db.get(PluginPermission, {"plugin_name": plugin_name, "permission": permission})
        if row:
            row.granted = False
            await self.db.commit()

    async def get_plugin_permissions(self, plugin_name: str) -> list[PluginPermission]:
        """Return all permissions for a plugin."""
        rows = await self.db.scalars(select(PluginPermission).where(PluginPermission.plugin_name == plugin_name))
        return list(rows)
