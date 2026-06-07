"""Voice module orchestration for wake word, STT, and TTS."""

from enum import StrEnum

from core.event_bus import EventBus
from core.voice.stt import LocalSTT
from core.voice.tts import LocalTTS
from core.voice.wake_word import WakeWordListener


class VoiceState(StrEnum):
    """Voice module states."""

    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    WAITING = "waiting"
    SPEAKING = "speaking"


class VoiceModule:
    """Coordinates wake word detection, transcription, and speech output."""

    def __init__(self, event_bus: EventBus) -> None:
        """Create the voice module."""
        self.event_bus = event_bus
        self.state = VoiceState.IDLE
        self.stt = LocalSTT()
        self.tts = LocalTTS()
        self.wake_word = WakeWordListener(event_bus)

    async def start(self) -> None:
        """Start the voice module."""
        self.wake_word.start()
        await self.event_bus.publish("voice.status", {"state": self.state.value})

    async def speak_response(self, payload: dict) -> None:
        """Speak an AI response event."""
        self.state = VoiceState.SPEAKING
        await self.event_bus.publish("voice.status", {"state": self.state.value})
        await self.tts.speak(payload.get("text", ""))
        self.state = VoiceState.IDLE
        await self.event_bus.publish("voice.status", {"state": self.state.value})
