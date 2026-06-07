"""Example external Sanaya plugin."""

from core.automation.plugin_base import PluginManifest, SanayaPlugin


class ExamplePlugin(SanayaPlugin):
    """Example plugin authors can copy."""

    manifest = PluginManifest("example_plugin", "Example user plugin", "1.0.0", ["example"], [], False)

    async def execute(self, command: str, params: dict, context: dict) -> dict:
        """Return an example response."""
        return {"success": True, "result": {"command": command, "params": params, "context": context}, "message": "Example plugin executed."}
