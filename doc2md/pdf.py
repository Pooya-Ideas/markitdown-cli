"""PDF conversion with quality scoring and Farsi post-processing."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple

from doc2md.utils import PERSIAN_ARABIC_RE, ZWNJ, contains_persian_or_arabic

logger = logging.getLogger("doc2md.pdf")

_BAD_CONTROLS = re.compile(r"[\u200b\u200d\u202a-\u202e\ufeff]")
_ARABIC_LETTER = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+"
)
_FA_CHAR = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
_SOFT_BREAK = re.compile(
    r"([\u0600-\u06FF])\s*[-\u00ad\u2010\u2011]\s*\n\s*([\u0600-\u06FF])"
)
_SECTION_NUM = re.compile(
    r"(?m)(?<![\d\u0600-\u06FF])(\d{1,2})\s*[\n\r]+\s*([-–—])\s*[\n\r]+\s*(\d{1,2})(?![\d])"
)
_SECTION_NUM_PARTIAL = re.compile(
    r"(?m)(?<![\d])(\d{1,2})\s*([-–—])\s*[\n\r]+\s*(\d{1,2})(?![\d])"
)
_SECTION_NUM_TRIPLE = re.compile(
    r"(?m)(?<![\d])(\d{1,2})\s*[\n\r]+\s*(\d{1,2})\s*[\n\r]+\s*([-–—])\s*[\n\r]+\s*(\d{1,2})(?![\d])"
)
_MULTI_BLANK = re.compile(r"\n{3,}")


def pdf_quality_score(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    letters = [c for c in text if c.isalpha() or ("\u0600" <= c <= "\u06FF")]
    if not letters:
        return 0.05
    fa_count = sum(1 for c in letters if PERSIAN_ARABIC_RE.match(c))
    fa_ratio = fa_count / len(letters)
    zwnj_bonus = min(0.15, text.count(ZWNJ) / max(len(text), 1) * 50)
    tokens = text.split()
    if tokens:
        multi_ratio = sum(1 for t in tokens if len(t) > 1) / len(tokens)
        avg_len = sum(len(t) for t in tokens) / len(tokens)
    else:
        multi_ratio = 0.0
        avg_len = 0.0
    bad = len(_BAD_CONTROLS.findall(text))
    control_penalty = min(0.3, bad / max(len(text), 1) * 20)
    length_bonus = min(0.15, avg_len / 20.0)
    nl_penalty = min(0.2, text.count("\n") / max(len(text), 1) * 5)
    score = (
        0.35 * fa_ratio + 0.25 * multi_ratio
        + 0.15 * (1.0 if contains_persian_or_arabic(text) else 0.0)
        + zwnj_bonus + length_bonus - control_penalty - nl_penalty
    )
    return max(0.0, min(1.0, score))


def phantom_nun_density(text: str) -> float:
    fa_tokens = re.findall(r"[\u0600-\u06FF\u200c]{3,}", text)
    if not fa_tokens:
        return 0.0
    bad = 0
    for tok in fa_tokens:
        n_count = tok.count("ن")
        if n_count >= 2 and n_count / len(tok) >= 0.25:
            bad += 1
    return bad / len(fa_tokens)


def _import_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        pass
    try:
        import fitz  # type: ignore
        return fitz
    except ImportError:
        return None


def extract_with_pymupdf(path: Path) -> Optional[str]:
    m = _import_pymupdf()
    if m is None:
        logger.debug("PyMuPDF not installed")
        return None
    try:
        doc = m.open(str(path))
        try:
            parts: List[str] = []
            for page in doc:
                blocks = page.get_text("blocks")
                if blocks:
                    blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
                    for b in blocks:
                        if len(b) > 4 and isinstance(b[4], str) and b[4].strip():
                            parts.append(b[4].strip())
                else:
                    parts.append(page.get_text("text"))
        finally:
            doc.close()
        return "\n\n".join(parts)
    except Exception as exc:
        logger.warning("PyMuPDF extraction failed: %s", exc)
        return None


def reverse_arabic_runs(text: str) -> str:
    def rev(match: re.Match) -> str:
        return match.group(0)[::-1]
    return _ARABIC_LETTER.sub(rev, text)


def join_spaced_fa_singles(text: str) -> str:
    tokens = text.split(" ")
    if len(tokens) < 3:
        return text
    out: List[str] = []
    buf: List[str] = []

    def flush() -> None:
        nonlocal buf
        if len(buf) >= 3:
            out.append("".join(buf)[::-1])
        else:
            out.extend(buf)
        buf = []

    for tok in tokens:
        if len(tok) == 1 and contains_persian_or_arabic(tok):
            buf.append(tok)
        else:
            flush()
            out.append(tok)
    flush()
    return " ".join(out)


def fix_section_numbers(text: str) -> str:
    text = _SECTION_NUM_TRIPLE.sub(r"\1-\2-\4", text)
    text = _SECTION_NUM.sub(r"\1\2\3", text)
    text = _SECTION_NUM_PARTIAL.sub(r"\1\2\3", text)
    return text


def fix_midword_newlines(text: str) -> str:
    text = _SOFT_BREAK.sub(r"\1\2", text)

    def _fix_line_wraps(s: str) -> str:
        lines = s.split("\n")
        if len(lines) <= 1:
            return s
        out = [lines[0]]
        for i in range(1, len(lines)):
            prev = out[-1]
            cur = lines[i]
            prev_r = prev.rstrip()
            cur_l = cur.lstrip()
            if (
                prev_r and cur_l
                and _FA_CHAR.search(prev_r[-1])
                and _FA_CHAR.search(cur_l[0])
            ):
                trail = re.search(r"[\u0600-\u06FF\u200c]+$", prev_r)
                lead = re.search(r"^[\u0600-\u06FF\u200c]+", cur_l)
                tlen = len(trail.group(0)) if trail else 0
                llen = len(lead.group(0)) if lead else 0
                if tlen <= 2 or llen <= 1:
                    out[-1] = prev_r + cur_l
                else:
                    out[-1] = prev_r + " " + cur_l
            else:
                out.append(cur)
        return "\n".join(out)

    prev = None
    for _ in range(6):
        prev = text
        text = _fix_line_wraps(text)
        if text == prev:
            break
    return text


def fix_compound_hyphen_breaks(text: str) -> str:
    zwnj = "\u200c"

    def _join(m: re.Match) -> str:
        return m.group(1) + zwnj + m.group(2)

    text = re.sub(
        r"([\u0600-\u06FF])\s*[-–—]\s*\n\s*([\u0600-\u06FF])",
        _join,
        text,
    )
    text = re.sub(
        r"([\u0600-\u06FF])\s+[-–—]\s+([\u0600-\u06FF])",
        _join,
        text,
    )
    return text


def collapse_excess_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip() + "\n"


def _line_stats(line: str) -> Tuple[float, float]:
    tokens = line.split()
    if not tokens:
        return 0.0, 0.0
    multi = sum(1 for t in tokens if len(t) > 1) / len(tokens)
    avg = sum(len(t) for t in tokens) / len(tokens)
    return multi, avg


def _looks_scrambled_fa_line(line: str) -> bool:
    if not contains_persian_or_arabic(line):
        return False
    tokens = line.split()
    if len(tokens) < 2:
        return False
    fa_tokens = [t for t in tokens if contains_persian_or_arabic(t)]
    if not fa_tokens:
        return False
    singles = sum(1 for t in fa_tokens if len(t) == 1)
    multi, avg = _line_stats(line)
    if singles / max(len(fa_tokens), 1) >= 0.4:
        return True
    if multi < 0.5 and avg < 3.0:
        return True
    if avg < 2.2 and len(fa_tokens) >= 3:
        return True
    return False


def _fix_line(line: str) -> str:
    if not contains_persian_or_arabic(line) or not line.strip():
        return line
    candidates = [
        line,
        reverse_arabic_runs(line),
        join_spaced_fa_singles(line),
        reverse_arabic_runs(join_spaced_fa_singles(line)),
        line[::-1],
    ]

    def rank(s: str) -> Tuple[float, float]:
        multi, avg = _line_stats(s)
        return (pdf_quality_score(s), multi * 0.5 + min(avg, 8) * 0.05)

    return max(candidates, key=rank)


def maybe_fix_pdf_rtl(text: str) -> str:
    if not contains_persian_or_arabic(text):
        return text
    lines = text.splitlines()
    out: List[str] = []
    fixed_count = 0
    for line in lines:
        if not contains_persian_or_arabic(line):
            out.append(line)
            continue
        repaired = _fix_line(line)
        if repaired != line:
            if _looks_scrambled_fa_line(line) or pdf_quality_score(repaired) > pdf_quality_score(line) + 0.02:
                out.append(repaired)
                fixed_count += 1
            else:
                out.append(line)
        else:
            out.append(line)
    if fixed_count:
        logger.info("PDF RTL normalize: repaired %d line(s)", fixed_count)
    return "\n".join(out)


def cleanup_pdf_text(text: str) -> str:
    if not text:
        return text
    text = fix_section_numbers(text)
    text = fix_midword_newlines(text)
    text = fix_compound_hyphen_breaks(text)
    text = maybe_fix_pdf_rtl(text)
    text = fix_section_numbers(text)
    text = fix_midword_newlines(text)
    text = collapse_excess_whitespace(text)
    density = phantom_nun_density(text)
    if density >= 0.08:
        logger.warning(
            "High PDF font-artifact density (%.0f%%). "
            "Some letters may be wrong (common with Farsi PDF fonts). "
            "Prefer converting the original Word (.docx) file, or use OCR.",
            density * 100,
        )
    return text


def convert_pdf_smart(
    path: Path,
    markitdown_text: str,
    *,
    rtl_mode: str = "none",
) -> str:
    from doc2md.rtl import fix_rtl_text

    candidates: List[Tuple[str, str, float]] = []
    if markitdown_text and markitdown_text.strip():
        t = cleanup_pdf_text(markitdown_text)
        candidates.append(("markitdown", t, pdf_quality_score(t)))
    alt = extract_with_pymupdf(path)
    if alt and alt.strip():
        t = cleanup_pdf_text(alt)
        candidates.append(("pymupdf", t, pdf_quality_score(t)))
    if not candidates:
        logger.warning("No PDF text could be extracted from %s", path)
        return markitdown_text or ""
    best_name, best_text, best_score = max(candidates, key=lambda x: x[2])
    for name, _text, score in candidates:
        logger.info("PDF quality %s: %.3f", name, score)
    logger.info("Selected PDF extractor: %s (score=%.3f)", best_name, best_score)
    return fix_rtl_text(best_text, mode=rtl_mode)
