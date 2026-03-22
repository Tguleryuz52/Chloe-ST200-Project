"""WAV helpers and alignment → viseme timeline (heuristic)."""

from __future__ import annotations

import io
import logging
import wave
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Oculus-style viseme ids (MetaHuman / lip-sync friendly labels; tune in AnimBP).
_VISEME_BY_CHAR: dict[str, str] = {
    " ": "sil",
    "\n": "sil",
    "\t": "sil",
    ".": "sil",
    ",": "sil",
    "!": "sil",
    "?": "sil",
    ":": "sil",
    ";": "sil",
    "a": "aa",
    "e": "E",
    "i": "I",
    "ı": "I",
    "o": "O",
    "ö": "O",
    "u": "U",
    "ü": "U",
    "b": "PP",
    "m": "PP",
    "p": "PP",
    "f": "FF",
    "v": "FF",
    "w": "FF",
    "d": "DD",
    "t": "DD",
    "n": "nn",
    "l": "nn",
    "r": "RR",
    "s": "SS",
    "ş": "CH",
    "ç": "CH",
    "c": "CH",
    "k": "kk",
    "g": "kk",
    "ğ": "kk",
    "h": "kk",
    "j": "CH",
    "y": "I",
    "z": "SS",
    "q": "kk",
    "x": "SS",
}


def _char_viseme(ch: str) -> str:
    if not ch:
        return "sil"
    lower = ch.lower()
    if lower in _VISEME_BY_CHAR:
        return _VISEME_BY_CHAR[lower]
    return "sil"


def alignment_to_visemes(alignment: dict[str, Any] | None) -> list[dict[str, Any]]:
    """
    Build a timeline from ElevenLabs character alignment.
    Each entry: {"t": float_seconds, "v": viseme_id}
    """
    if not alignment:
        return []
    try:
        chars = alignment.get("characters") or []
        starts = alignment.get("character_start_times_seconds") or []
        if not chars or not starts:
            return []
        n = min(len(chars), len(starts))
        out: list[dict[str, Any]] = []
        last_v = ""
        for i in range(n):
            ch = chars[i] if i < len(chars) else ""
            t = float(starts[i]) if i < len(starts) else 0.0
            v = _char_viseme(ch)
            if v != last_v or not out:
                out.append({"t": t, "v": v})
                last_v = v
        return out
    except Exception as exc:
        logger.exception("alignment_to_visemes failed: %s", exc)
        return []


def write_wav_int16_mono(path: str, samples: np.ndarray, sample_rate: int) -> None:
    """Write int16 mono PCM to a standard WAV file."""
    try:
        if samples.dtype != np.int16:
            samples = samples.astype(np.int16)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples.tobytes())
    except Exception as exc:
        logger.exception("write_wav_int16_mono failed: %s", exc)
        raise


def wav_bytes_from_int16_mono(samples: np.ndarray, sample_rate: int) -> bytes:
    """Return WAV file bytes (for Whisper upload)."""
    try:
        if samples.dtype != np.int16:
            samples = samples.astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples.tobytes())
        return buf.getvalue()
    except Exception as exc:
        logger.exception("wav_bytes_from_int16_mono failed: %s", exc)
        raise
