"""Browser automation plugin using Playwright."""

from typing import Any

from playwright.async_api import async_playwright

from core.automation.plugin_base import PluginManifest, SanayaPlugin


class BrowserPlugin(SanayaPlugin):
    """Open URLs and searches in a persistent browser."""

    manifest = PluginManifest("browser_plugin", "Open websites and searches", "1.0.0", ["search", "go to", "open website", "browse", "navigate"], ["browser.open", "browser.navigate"], False)
    browser = None

    async def execute(self, command: str, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Open a URL or search query."""
        _ = command, context
        query = params.get("query") or params.get("url") or "https://www.google.com"
        url = query if str(query).startswith("http") else f"https://www.google.com/search?q={query}"
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        return {"success": True, "result": url, "message": "Browser opened."}
