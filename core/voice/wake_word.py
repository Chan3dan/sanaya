"""Wake word listener for 'Hey Sanaya'."""

import threading
from pathlib import Path

from loguru import logger

from core.config import config
from core.event_bus import EventBus


class WakeWordListener:
    """Background wake word listener."""

    def __init__(self, event_bus: EventBus, model_path: Path = config.wake_word_model) -> None:
        """Create listener for a wake word model."""
        self.event_bus = event_bus
        self.model_path = model_path
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        """Start background wake word detection."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background wake word detection."""
        self._running = False

    def _run(self) -> None:
        """Run the listener loop."""
        logger.info("Wake word listener ready")
        while self._running:
            threading.Event().wait(1)
