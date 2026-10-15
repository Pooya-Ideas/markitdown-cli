"""RTL (Persian/Arabic) helpers.

IMPORTANT: Do NOT apply python-bidi get_display() to text that will be stored
in Markdown files. get_display() produces *visual* order for terminal/GUI
rendering and corrupts logical order for editors and LLMs.

Default behaviour: leave text in logical order (correct for Markdown).
Optional --rtl-visual: apply get_display for display-only pipelines.
"""

from __future__ import annotations

import logging
from typing import Optional

from doc2md.utils import contains_persian_or_arabic

logger = logging.getLogger("doc2md.rtl")

RLM = "\u200f"
LRM = "\u200e"


def fix_rtl_text(
    text: str,
    *,
    mode: str = "none",
) -> str:
    """Optionally adjust RTL text.

    Modes:
      - none: return text unchanged (recommended for Markdown files)
      - marks: wrap lines that contain Persian/Arabic with RLM
      - visual: apply python-bidi get_display (NOT for saving to files)
    """
    if not text or mode in ("none", "off", "no"):
        return text

    if mode == "marks":
        lines = []
        for line in text.splitlines():
            if contains_persian_or_arabic(line):
                lines.append(RLM + line if not line.startswith(RLM) else line)
            else:
                lines.append(line)
        return "\n".join(lines)

    if mode == "visual":
        try:
            from bidi.algorithm import get_display
        except ImportError:
            logger.warning(
                "python-bidi not installed; cannot apply --rtl-visual. "
                "Install with: pip install python-bidi"
            )
            return text
        lines = []
        for line in text.splitlines():
            if contains_persian_or_arabic(line):
                lines.append(get_display(line))
            else:
                lines.append(line)
        logger.warning(
            "Applied visual RTL reordering (--rtl-visual). "
            "This changes character order and may confuse LLMs/editors."
        )
        return "\n".join(lines)

    logger.warning("Unknown RTL mode %r; leaving text unchanged.", mode)
    return text


def resolve_rtl_mode(
    *,
    rtl_visual: bool = False,
    no_rtl_fix: bool = False,
    rtl_mode: Optional[str] = None,
) -> str:
    """Resolve effective RTL mode from CLI flags."""
    if no_rtl_fix:
        return "none"
    if rtl_mode:
        return rtl_mode.lower().strip()
    if rtl_visual:
        return "visual"
    return "none"
