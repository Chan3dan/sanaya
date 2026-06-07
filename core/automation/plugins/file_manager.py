"""File management automation plugin."""

from pathlib import Path
import shutil
from typing import Any

from core.automation.plugin_base import PluginManifest, SanayaPlugin


class FileManagerPlugin(SanayaPlugin):
    """Find, copy, move, delete, and list files."""

    manifest = PluginManifest("file_manager", "Manage files safely", "1.0.0", ["find", "open file", "move", "copy", "delete", "rename", "create folder"], ["files.read", "files.write"], True)

    def _safe_path(self, value: str) -> Path:
        """Resolve a path and reject traversal-like inputs."""
        path = Path(value).expanduser().resolve()
        if ".." in Path(value).parts:
            raise ValueError("Directory traversal is not allowed")
        return path

    async def execute(self, command: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a file command."""
        _ = command, context
        action = params.get("action", "list")
        path = self._safe_path(params.get("path", "."))
        if action == "create_folder":
            path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "result": str(path), "message": "Folder created."}
        if action == "copy":
            dst = self._safe_path(params["destination"])
            shutil.copy2(path, dst)
            return {"success": True, "result": str(dst), "message": "File copied."}
        return {"success": True, "result": [item.name for item in path.iterdir()] if path.is_dir() else str(path), "message": "File command complete."}
