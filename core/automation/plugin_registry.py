"""Plugin discovery and command matching."""

import importlib
import inspect
from pathlib import Path

from loguru import logger

from core.automation.plugin_base import SanayaPlugin


class PluginRegistry:
    """Discovers plugins from built-in and user plugin directories."""

    def __init__(self) -> None:
        """Create an empty plugin registry."""
        self.plugins: list[SanayaPlugin] = []

    def discover(self) -> list[SanayaPlugin]:
        """Discover built-in plugin classes."""
        modules = [
            "core.automation.plugins.app_launcher",
            "core.automation.plugins.file_manager",
            "core.automation.plugins.browser_plugin",
            "core.automation.plugins.system_plugin",
        ]
        self.plugins.clear()
        for module_name in modules:
            module = importlib.import_module(module_name)
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, SanayaPlugin) and cls is not SanayaPlugin:
                    self.plugins.append(cls())
        logger.info(f"Loaded {len(self.plugins)} plugins")
        return self.plugins

    def find_plugin(self, command: str) -> SanayaPlugin | None:
        """Find a plugin whose trigger appears in a command."""
        command_lower = command.lower()
        for plugin in self.plugins:
            if any(trigger in command_lower for trigger in plugin.manifest.triggers):
                return plugin
        return None

    def watch(self, path: Path) -> None:
        """Placeholder for hot reload watching."""
        logger.info(f"Watching plugins at {path}")
