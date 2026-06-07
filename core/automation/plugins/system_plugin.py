"""Windows system automation plugin."""

import ctypes
from pathlib import Path
import subprocess
from typing import Any

import pyautogui

from core.automation.plugin_base import PluginManifest, SanayaPlugin


class SystemPlugin(SanayaPlugin):
    """Perform selected Windows system actions."""

    manifest = PluginManifest("system_plugin", "Control system features", "1.0.0", ["volume", "brightness", "screenshot", "sleep", "lock screen"], ["os.system"], False)

    async def execute(self, command: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a Windows system command."""
        _ = params, context
        if "screenshot" in command.lower():
            folder = Path.home() / "Desktop" / "Sanaya" / "Screenshots"
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / "screenshot.png"
            pyautogui.screenshot(str(target))
            return {"success": True, "result": str(target), "message": "Screenshot saved."}
        if "lock" in command.lower():
            ctypes.windll.user32.LockWorkStation()
            return {"success": True, "result": None, "message": "Screen locked."}
        if "sleep" in command.lower():
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=False)
            return {"success": True, "result": None, "message": "Sleep requested."}
        return {"success": False, "result": None, "message": "Unsupported system command."}
