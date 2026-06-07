"""Base contracts for Sanaya AI providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    """A provider-agnostic chat message."""

    role: str
    content: str


@dataclass(slots=True)
class ProviderCapabilities:
    """Feature and cost metadata for an AI provider."""

    supports_vision: bool
    supports_streaming: bool
    max_context_tokens: int
    cost_per_1k_tokens: float
    is_local: bool


class AIProvider(ABC):
    """Abstract interface all AI providers must implement."""

    name: str

    @abstractmethod
    async def chat(self, messages: list[Message], options: dict) -> AsyncGenerator[str, None]:
        """Stream a chat response."""
        yield ""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector."""

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities."""
