"""Speech-to-text engines for Sanaya."""

from abc import ABC, abstractmethod

from faster_whisper import WhisperModel

from core.config import config


class STTEngine(ABC):
    """Abstract speech-to-text engine."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text."""


class LocalSTT(STTEngine):
    """Local faster-whisper speech-to-text."""

    def __init__(self) -> None:
        """Load the configured Whisper model."""
        self.model = WhisperModel(config.whisper_model, device="cpu", compute_type="int8")

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text."""
        return ""

    async def record_until_silence(self) -> bytes:
        """Record microphone audio until silence is detected."""
        return b""


class CloudSTT(STTEngine):
    """Future cloud STT provider placeholder."""

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe with a future cloud provider."""
        raise NotImplementedError("Cloud STT is planned for a later phase")
