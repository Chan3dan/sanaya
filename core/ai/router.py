"""AIRouter selects providers without exposing provider SDKs to modules."""

from loguru import logger

from core.ai.base_provider import AIProvider
from core.ai.providers.claude_provider import ClaudeProvider
from core.ai.providers.gemini_provider import GeminiProvider
from core.ai.providers.ollama_provider import OllamaProvider
from core.ai.providers.openai_provider import OpenAIProvider
from core.config import config
from core.security.privacy_router import PrivacyRouter


class AIRouter:
    """Routes AI work to local or cloud providers by task and privacy."""

    def __init__(self) -> None:
        """Instantiate available providers."""
        self.providers: dict[str, AIProvider] = {
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "claude": ClaudeProvider(),
        }
        self.privacy_router = PrivacyRouter()

    def select_provider(self, task_type: str, privacy_required: bool, context: dict) -> AIProvider:
        """Select a provider according to Sanaya routing rules."""
        if privacy_required or self.privacy_router.requires_local({**context, "task_type": task_type}):
            reason = "privacy/local rule"
            provider = self.providers["ollama"]
        elif task_type == "vision":
            reason = "vision task"
            provider = self.providers["gemini"]
        elif task_type in {"complex_reasoning", "code"}:
            reason = "reasoning/code task"
            provider = self.providers["claude"]
        elif task_type == "embedding":
            reason = "local embeddings"
            provider = self.providers["ollama"]
        else:
            reason = "default provider"
            provider = self.providers[config.default_ai_provider]
        logger.info(f"AI provider selected: {provider.name} ({reason})")
        return provider

    async def stream_chat(self, messages: list, task_type: str = "chat", privacy_required: bool = False, context: dict | None = None):
        """Stream chat tokens with Ollama fallback."""
        provider = self.select_provider(task_type, privacy_required, context or {})
        try:
            async for token in provider.chat(messages, {}):
                yield token
        except Exception as exc:
            logger.warning(f"Provider {provider.name} failed, falling back to Ollama: {exc}")
            async for token in self.providers["ollama"].chat(messages, {}):
                yield token
