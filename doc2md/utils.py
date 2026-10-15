"""Shared helpers for Markitdown-CLI."""

from __future__ import annotations

import logging
import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator, Optional, Set

logger = logging.getLogger("doc2md")

PERSIAN_ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
ZWNJ = "\u200c"

SUPPORTED_DOC_EXTENSIONS: Set[str] = {
    ".docx", ".pptx", ".xlsx", ".xls",
    ".pdf",
    ".html", ".htm",
    ".csv", ".json", ".xml",
    ".txt", ".md",
    ".epub",
    ".msg",
}


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        stream=sys.stderr,
        force=True,
    )


def contains_persian_or_arabic(text: str) -> bool:
    return bool(PERSIAN_ARABIC_RE.search(text or ""))


def parse_extensions(ext_arg: Optional[str]) -> Optional[Set[str]]:
    if not ext_arg or ext_arg.strip().lower() in {"all", "*"}:
        return None
    result: Set[str] = set()
    for part in ext_arg.split(","):
        part = part.strip().lower().lstrip(".")
        if part:
            result.add("." + part)
    return result or None


def ensure_utf8_stdio() -> None:
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


@contextmanager
def elapsed_timer() -> Iterator[list]:
    start = time.perf_counter()
    box: list = []
    try:
        yield box
    finally:
        box.append(time.perf_counter() - start)


def iter_files(
    root: Path,
    *,
    recursive: bool = True,
    extensions: Optional[Set[str]] = None,
) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for path in sorted(root.glob(pattern)):
        if not path.is_file():
            continue
        if extensions is not None and path.suffix.lower() not in extensions:
            continue
        yield path


def output_path_for(
    input_path: Path,
    *,
    output_dir: Optional[Path] = None,
    root: Optional[Path] = None,
    suffix: str = ".md",
) -> Path:
    if output_dir is None:
        return input_path.with_suffix(suffix)
    output_dir = output_dir.expanduser().resolve()
    if root is not None:
        try:
            rel = input_path.resolve().relative_to(root.resolve())
        except ValueError:
            rel = Path(input_path.name)
    else:
        rel = Path(input_path.name)
    out = output_dir / rel.with_suffix(suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out
