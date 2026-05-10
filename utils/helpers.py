"""
utils/helpers.py
Reusable utility functions used across the project.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Optional


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a consistent format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# ── Text helpers ──────────────────────────────────────────────────────────────

def truncate(text: str, max_chars: int = 120, ellipsis: str = "…") -> str:
    """Truncate *text* to *max_chars*, appending *ellipsis* if needed."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(ellipsis)] + ellipsis


def is_bengali(text: str) -> bool:
    """Return True if *text* contains at least one Bengali Unicode character."""
    return any("\u0980" <= ch <= "\u09FF" for ch in text)


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Strip whitespace and cap length."""
    return text.strip()[:max_length]


# ── Time helpers ──────────────────────────────────────────────────────────────

def friendly_timestamp(dt: Optional[datetime] = None) -> str:
    """Return a human-readable timestamp string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%d %b %Y, %I:%M %p")


def time_ago(dt: datetime) -> str:
    """
    Return a relative time string like '২ মিনিট আগে' (2 minutes ago).
    Falls back to the formatted date for old records.
    """
    delta = datetime.utcnow() - dt
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "এইমাত্র"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} মিনিট আগে"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ঘন্টা আগে"
    return friendly_timestamp(dt)


# ── Quick-reply suggestions ───────────────────────────────────────────────────

QUICK_REPLIES: list[str] = [
    "আমার অর্ডারের অবস্থা কী?",
    "পণ্য রিটার্ন কীভাবে করব?",
    "ডেলিভারি চার্জ কত?",
    "কোন পেমেন্ট পদ্ধতি গ্রহণযোগ্য?",
    "সেরা অফার দেখান",
    "What is your return policy?",
    "How long does delivery take?",
]
