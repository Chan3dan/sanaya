"""Gemini provider implementation."""

from collections.abc import AsyncGenerator

import google.generativeai as genai

from core.ai.base_provider import AIProvider, Message, ProviderCapabilities
from core.db.session import SessionLocal
from core.security.key_manager import KeyManager


class GeminiProvider(AIProvider):
    """Provider backed by Google Gemini."""

    name = "gemini"

    async def _configure(self) -> None:
        """Configure the Gemini SDK."""
        async with SessionLocal() as db:
            key = await KeyManager().get_api_key(db, self.name)
        genai.configure(api_key=key)

    async def chat(self, messages: list[Message], options: dict) -> AsyncGenerator[str, None]:
        """Stream a Gemini response."""
        await self._configure()
        model = genai.GenerativeModel(options.get("model", "gemini-2.0-flash"))
        prompt = "\n".join(f"{message.role}: {message.content}" for message in messages)
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def embed(self, text: str) -> list[float]:
        """Return a Gemini embedding."""
        await self._configure()
        response = genai.embed_content(model="models/text-embedding-004", content=text)
        return list(response["embedding"])

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Gemini capability metadata."""
        return ProviderCapabilities(True, True, 1000000, 0.001, False)
