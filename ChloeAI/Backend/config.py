"""Load environment and resolved paths for ChloeAI backend."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent
_CHLOEAI_ROOT = _BACKEND_DIR.parent

load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_CHLOEAI_ROOT / ".env")


def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v is not None and v.strip() != "":
        return v
    return default


def _env_int(key: str, default: int) -> int:
    raw = _env(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = _env(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


OPENAI_API_KEY = _env("OPENAI_API_KEY")
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = _env("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = _env("ELEVENLABS_VOICE_ID")

CLAUDE_MODEL = _env("CLAUDE_MODEL", "claude-sonnet-4-20250514")
WHISPER_MODEL = _env("WHISPER_MODEL", "whisper-1")
ELEVENLABS_MODEL_ID = _env("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

WHISPER_LANGUAGE = _env("WHISPER_LANGUAGE", "tr")

WS_HOST = _env("WS_HOST", "127.0.0.1") or "127.0.0.1"
WS_PORT = _env_int("WS_PORT", 8765)

_audio_dir = _env("AUDIO_OUTPUT_DIR")
if _audio_dir:
    AUDIO_OUTPUT_DIR = Path(_audio_dir).expanduser().resolve()
else:
    AUDIO_OUTPUT_DIR = (_CHLOEAI_ROOT / "Audio").resolve()

PROMPTS_DIR = (_CHLOEAI_ROOT / "Prompts").resolve()
CHLOE_PERSONALITY_PATH = (PROMPTS_DIR / "chloe_personality.txt").resolve()

SAMPLE_RATE = _env_int("SAMPLE_RATE", 16000)
SILENCE_DURATION_MS = _env_int("SILENCE_DURATION_MS", 800)
MIN_SPEECH_MS = _env_int("MIN_SPEECH_MS", 400)
MIN_AUDIO_RMS = _env_float("MIN_AUDIO_RMS", 0.015)

LOG_LEVEL = _env("LOG_LEVEL", "INFO") or "INFO"


def setup_logging() -> None:
    try:
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    except Exception:
        logging.basicConfig(level=logging.INFO)


def validate_config() -> list[str]:
    """Return list of missing required keys (empty if OK)."""
    missing: list[str] = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not ELEVENLABS_API_KEY:
        missing.append("ELEVENLABS_API_KEY")
    if not ELEVENLABS_VOICE_ID:
        missing.append("ELEVENLABS_VOICE_ID")
    return missing
