"""ElevenLabs TTS with timestamps + WAV file on disk."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any

import httpx

from . import config

logger = logging.getLogger(__name__)

ELEVEN_BASE = "https://api.elevenlabs.io"


async def synthesize_with_timestamps(text: str) -> tuple[Path, dict[str, Any] | None]:
    """
    Call ElevenLabs with-timestamps, save WAV under AUDIO_OUTPUT_DIR.
    Returns (absolute_path_to_wav, alignment_dict_or_none).
    """
    try:
        t = (text or "").strip()
        if not t:
            raise ValueError("empty text for TTS")
        if not config.ELEVENLABS_API_KEY or not config.ELEVENLABS_VOICE_ID:
            raise RuntimeError("ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID missing")

        config.AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = (config.AUDIO_OUTPUT_DIR / "response.wav").resolve()

        url = f"{ELEVEN_BASE}/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}/with-timestamps"
        headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "text": t,
            "model_id": config.ELEVENLABS_MODEL_ID,
        }
        params = {"output_format": "wav_44100"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, headers=headers, json=body, params=params)
            r.raise_for_status()
            payload = r.json()

        audio_b64 = payload.get("audio_base64") or ""
        raw = base64.b64decode(audio_b64)
        alignment = payload.get("alignment")

        out_path.write_bytes(raw)

        return out_path, alignment if isinstance(alignment, dict) else None
    except Exception as exc:
        logger.exception("synthesize_with_timestamps failed: %s", exc)
        raise
