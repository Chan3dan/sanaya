"""Claude provider implementation."""

from collections.abc import AsyncGenerator

from anthropic import AsyncAnthropic

from core.ai.base_provider import AIProvider, Message, ProviderCapabilities
from core.db.session import SessionLocal
from core.security.key_manager import KeyManager


class ClaudeProvider(AIProvider):
    """Provider backed by Anthropic Claude."""

    name = "claude"

    async def _client(self) -> AsyncAnthropic:
        """Create an authenticated Anthropic client."""
        async with SessionLocal() as db:
            key = await KeyManager().get_api_key(db, self.name)
        return AsyncAnthropic(api_key=key)

    async def chat(self, messages: list[Message], options: dict) -> AsyncGenerator[str, None]:
        """Stream a Claude response."""
        client = await self._client()
        system = "\n".join(message.content for message in messages if message.role == "system")
        user_messages = [{"role": message.role, "content": message.content} for message in messages if message.role != "system"]
        async with client.messages.stream(
            model=options.get("model", "claude-sonnet-4-6"),
            max_tokens=options.get("max_tokens", 1024),
            system=system or None,
            messages=user_messages,
        ) as stream:
            async for token in stream.text_stream:
                yield token

    async def embed(self, text: str) -> list[float]:
        """Claude does not expose embeddings in this MVP."""
        raise NotImplementedError("Claude embeddings are not supported")

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Claude capability metadata."""
        return ProviderCapabilities(True, True, 200000, 0.015, False)
