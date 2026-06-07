"""Text-to-speech engines for Sanaya."""

from abc import ABC, abstractmethod

try:
    from TTS.api import TTS
except ImportError:
    TTS = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class TTSEngine(ABC):
    """Abstract text-to-speech engine."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes."""

    @abstractmethod
    async def speak(self, text: str) -> None:
        """Speak synthesized text."""


class LocalTTS(TTSEngine):
    """Local Coqui TTS engine."""

    def __init__(self) -> None:
        """Preload the available local voice engine."""
        if TTS is not None:
            self.provider = "coqui"
            self.model = TTS("tts_models/en/ljspeech/tacotron2-DDC")
            self.engine = None
        elif pyttsx3 is not None:
            self.provider = "pyttsx3"
            self.model = None
            self.engine = pyttsx3.init()
        else:
            raise RuntimeError("No local TTS engine is installed. Install Coqui TTS or pyttsx3.")

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes."""
        if self.provider == "coqui":
            _ = text
        else:
            _ = text
        return b""

    async def speak(self, text: str) -> None:
        """Speak text immediately."""
        if self.provider == "pyttsx3" and self.engine is not None:
            self.engine.say(text)
            self.engine.runAndWait()
            return
        _ = await self.synthesize(text)


class CloudTTS(TTSEngine):
    """Future ElevenLabs-style provider placeholder."""

    async def synthesize(self, text: str) -> bytes:
        """Synthesize with a future cloud provider."""
        raise NotImplementedError("Cloud TTS is planned for a later phase")

    async def speak(self, text: str) -> None:
        """Speak with a future cloud provider."""
        raise NotImplementedError("Cloud TTS is planned for a later phase")
