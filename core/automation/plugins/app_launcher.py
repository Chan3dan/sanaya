"""Windows app launcher plugin."""

import subprocess
from typing import Any

from core.automation.plugin_base import PluginManifest, SanayaPlugin


class AppLauncherPlugin(SanayaPlugin):
    """Launch common Windows applications."""

    manifest = PluginManifest("app_launcher", "Open desktop apps", "1.0.0", ["open", "launch", "start", "run"], ["os.launch"], False)
    app_map = {"chrome": "chrome.exe", "notepad": "notepad.exe", "calculator": "calc.exe"}

    async def execute(self, command: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Launch the requested app."""
        _ = params, context
        app = next((name for name in self.app_map if name in command.lower()), "")
        if not app:
            return {"success": False, "result": None, "message": "I could not identify the app to open."}
        subprocess.Popen([self.app_map[app]], shell=False)
        return {"success": True, "result": app, "message": f"I've opened {app} for you."}
