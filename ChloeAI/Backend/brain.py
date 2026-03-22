"""Claude (Anthropic) chat — Chloe personality."""

from __future__ import annotations

import logging
from pathlib import Path

from anthropic import AsyncAnthropic

from . import config

logger = logging.getLogger(__name__)


def _load_system_prompt() -> str:
    try:
        path = Path(config.CHLOE_PERSONALITY_PATH)
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger.exception("Failed to read personality file: %s", exc)
    return (
        "Sen Chloe adında sakin ve zeki bir androidsin. "
        "Kısa ve net Türkçe cevap ver."
    )


async def reply_as_chloe(user_text: str) -> str:
    """Send user message to Claude with Chloe system prompt; return assistant text."""
    try:
        text = (user_text or "").strip()
        if not text:
            return ""
        if not config.ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY is not set")
            return ""
        client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        system = _load_system_prompt()
        msg = await client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": text}],
        )
        parts: list[str] = []
        for block in getattr(msg, "content", None) or []:
            btype = getattr(block, "type", None)
            if btype == "text":
                parts.append(getattr(block, "text", "") or "")
        out = "".join(parts).strip()
        return out
    except Exception as exc:
        logger.exception("reply_as_chloe failed: %s", exc)
        return ""
