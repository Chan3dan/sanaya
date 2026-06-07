"""Local Ollama provider for private chat and embeddings."""

from collections.abc import AsyncGenerator

import ollama

from core.ai.base_provider import AIProvider, Message, ProviderCapabilities
from core.config import config


class OllamaProvider(AIProvider):
    """Provider backed by local Ollama models."""

    name = "ollama"

    async def chat(self, messages: list[Message], options: dict) -> AsyncGenerator[str, None]:
        """Stream a chat response from Ollama."""
        payload = [{"role": message.role, "content": message.content} for message in messages]
        stream = ollama.chat(model=options.get("model", config.ollama_chat_model), messages=payload, stream=True)
        for chunk in stream:
            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token

    async def embed(self, text: str) -> list[float]:
        """Return a local embedding."""
        response = ollama.embeddings(model=config.embedding_model, prompt=text)
        return list(response.get("embedding", []))

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Ollama capability metadata."""
        return ProviderCapabilities(False, True, 8192, 0.0, True)
