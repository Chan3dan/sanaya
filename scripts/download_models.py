"""Download and warm up local models needed by Sanaya Phase 1."""

import subprocess
from pathlib import Path

from loguru import logger


def run(command: list[str]) -> None:
    """Run a model download command and log failures clearly."""
    logger.info("Running: {}", " ".join(command))
    try:
        subprocess.run(command, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning("Model command skipped or failed: {}", exc)


def main() -> None:
    """Create model directories and pull Ollama models."""
    Path("data/models/wake_word").mkdir(parents=True, exist_ok=True)
    Path("data/chroma").mkdir(parents=True, exist_ok=True)
    Path("data/sqlite").mkdir(parents=True, exist_ok=True)
    run(["ollama", "pull", "mistral:7b-q4"])
    run(["ollama", "pull", "nomic-embed-text"])
    logger.info("Whisper and Coqui models download on first library use.")
    logger.info("Place hey_sanaya.onnx at data/models/wake_word/hey_sanaya.onnx when available.")


if __name__ == "__main__":
    main()
