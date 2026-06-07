"""OpenAI provider implementation."""

from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from core.ai.base_provider import AIProvider, Message, ProviderCapabilities
from core.db.session import SessionLocal
from core.security.key_manager import KeyManager


class OpenAIProvider(AIProvider):
    """Provider backed by OpenAI chat and embedding APIs."""

    name = "openai"

    async def _client(self) -> AsyncOpenAI:
        """Create an authenticated OpenAI client."""
        async with SessionLocal() as db:
            key = await KeyManager().get_api_key(db, self.name)
        return AsyncOpenAI(api_key=key)

    async def chat(self, messages: list[Message], options: dict) -> AsyncGenerator[str, None]:
        """Stream a chat response from OpenAI."""
        client = await self._client()
        stream = await client.chat.completions.create(
            model=options.get("model", "gpt-4o-mini"),
            messages=[{"role": message.role, "content": message.content} for message in messages],
            stream=True,
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token

    async def embed(self, text: str) -> list[float]:
        """Return an OpenAI embedding."""
        client = await self._client()
        response = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding

    def get_capabilities(self) -> ProviderCapabilities:
        """Return OpenAI capability metadata."""
        return ProviderCapabilities(True, True, 128000, 0.005, False)
