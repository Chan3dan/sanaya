"""Base contracts for Sanaya automation plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PluginManifest:
    """Metadata for a Sanaya plugin."""

    name: str
    description: str
    version: str
    triggers: list[str]
    permissions: list[str]
    supports_undo: bool


class SanayaPlugin(ABC):
    """Base class for all Sanaya automation plugins."""

    manifest: PluginManifest

    @abstractmethod
    async def execute(self, command: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a plugin command."""

    async def undo(self, execution_id: str) -> bool:
        """Undo a plugin execution when supported."""
        _ = execution_id
        return False

    async def validate(self, params: dict[str, Any]) -> tuple[bool, str]:
        """Validate plugin parameters."""
        _ = params
        return True, ""
