"""ChloeAI backend: mic → Whisper → Claude → ElevenLabs → WebSocket → Unreal."""

from __future__ import annotations

import asyncio
import logging
import sys

import numpy as np
import sounddevice as sd
import websockets

from . import config
from .audio_utils import alignment_to_visemes, wav_bytes_from_int16_mono
from .brain import reply_as_chloe
from .stt import transcribe_wav_bytes
from .tts import synthesize_with_timestamps
from .websocket_server import broadcast_speech, handle_client

logger = logging.getLogger(__name__)


def _record_utterance_blocking() -> bytes:
    """Record until silence after speech; return WAV bytes (mono int16)."""
    try:
        sr = config.SAMPLE_RATE
        chunk_ms = 50
        chunk_samples = max(1, int(sr * chunk_ms / 1000.0))
        silence_needed = max(1, config.SILENCE_DURATION_MS // chunk_ms)
        min_speech_chunks = max(1, config.MIN_SPEECH_MS // chunk_ms)
        max_after_speech = int(120_000 / chunk_ms)

        chunks: list[np.ndarray] = []
        speech_chunks = 0
        silence_run = 0
        started = False
        after_start = 0

        while True:
            chunk = sd.rec(
                chunk_samples,
                samplerate=sr,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            rms = float(np.sqrt(np.mean(np.square(chunk))))
            is_voice = rms >= config.MIN_AUDIO_RMS

            if not started:
                if is_voice:
                    started = True
                    speech_chunks = 1
                    silence_run = 0
                    chunks.append(chunk)
                continue

            after_start += 1
            if is_voice:
                speech_chunks += 1
                silence_run = 0
                chunks.append(chunk)
            else:
                silence_run += 1
                chunks.append(chunk)
                if speech_chunks >= min_speech_chunks and silence_run >= silence_needed:
                    break

            if after_start >= max_after_speech:
                break

        if not chunks:
            return b""

        audio = np.concatenate(chunks, axis=0)
        audio = np.clip(audio, -1.0, 1.0)
        int16 = (audio * 32767.0).astype(np.int16)
        return wav_bytes_from_int16_mono(int16, sr)
    except Exception as exc:
        logger.exception("record_utterance_blocking failed: %s", exc)
        return b""


async def record_utterance() -> bytes:
    try:
        return await asyncio.to_thread(_record_utterance_blocking)
    except Exception as exc:
        logger.exception("record_utterance failed: %s", exc)
        return b""


async def run_once() -> None:
    """Single pipeline: STT → brain → TTS → broadcast."""
    try:
        wav = await record_utterance()
        if not wav:
            logger.debug("No audio captured; skipping.")
            return

        user_text = await transcribe_wav_bytes(wav, "user_utterance.wav")
        if not user_text:
            logger.warning("STT returned empty text.")
            return
        logger.info("User: %s", user_text[:200])

        answer = await reply_as_chloe(user_text)
        if not answer:
            logger.warning("Claude returned empty text.")
            return
        logger.info("Chloe: %s", answer[:200])

        wav_path, alignment = await synthesize_with_timestamps(answer)
        visemes = alignment_to_visemes(alignment)
        abs_audio = str(wav_path.resolve())

        await broadcast_speech(abs_audio, visemes, answer)
        logger.info("Broadcast speech: audio_path=%s", abs_audio)
    except Exception as exc:
        logger.exception("run_once failed: %s", exc)


async def mic_loop() -> None:
    logger.info("Listening — speak after silence, end with silence.")
    while True:
        try:
            await run_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("mic_loop iteration failed: %s", exc)


async def run() -> None:
    config.setup_logging()
    missing = config.validate_config()
    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        logger.error("Copy Backend/.env.example to Backend/.env and fill keys.")
        sys.exit(1)

    try:
        config.AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logger.exception("Could not create AUDIO_OUTPUT_DIR: %s", exc)
        sys.exit(1)

    logger.info(
        "Starting WebSocket on ws://%s:%s (connect Unreal before or after speaking)",
        config.WS_HOST,
        config.WS_PORT,
    )
    async with websockets.serve(
        handle_client,
        config.WS_HOST,
        config.WS_PORT,
    ):
        await mic_loop()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Interrupted.")
    except Exception as exc:
        logger.exception("Fatal: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
