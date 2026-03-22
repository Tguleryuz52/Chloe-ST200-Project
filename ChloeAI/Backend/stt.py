"""OpenAI Whisper speech-to-text."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from openai import AsyncOpenAI

from . import config

logger = logging.getLogger(__name__)


async def transcribe_wav_bytes(data: bytes, filename: str = "utterance.wav") -> str:
    """Transcribe WAV bytes; returns stripped text or empty string on failure."""
    try:
        if not data:
            return ""
        if not config.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set")
            return ""
        client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        bio = io.BytesIO(data)
        bio.name = filename
        kwargs: dict = {
            "model": config.WHISPER_MODEL,
            "file": bio,
        }
        lang = (config.WHISPER_LANGUAGE or "").strip()
        if lang:
            kwargs["language"] = lang
        result = await client.audio.transcriptions.create(**kwargs)
        text = getattr(result, "text", None) or ""
        return text.strip()
    except Exception as exc:
        logger.exception("transcribe_wav_bytes failed: %s", exc)
        return ""


async def transcribe_wav_file(path: Path | str) -> str:
    """Transcribe a WAV file on disk."""
    try:
        p = Path(path)
        if not p.is_file():
            logger.error("transcribe_wav_file: not a file: %s", p)
            return ""
        data = p.read_bytes()
        return await transcribe_wav_bytes(data, p.name)
    except Exception as exc:
        logger.exception("transcribe_wav_file failed: %s", exc)
        return ""
