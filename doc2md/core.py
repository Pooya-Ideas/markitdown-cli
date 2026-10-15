"""Core document conversion orchestration."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional, Set

from doc2md.images import embed_images
from doc2md.pdf import convert_pdf_smart
from doc2md.rtl import fix_rtl_text
from doc2md.utils import (
    SUPPORTED_DOC_EXTENSIONS,
    human_size,
    output_path_for,
    parse_extensions,
)

logger = logging.getLogger("doc2md.core")


def _markitdown_convert(path: Path) -> str:
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise RuntimeError(
            "markitdown is not installed. Run install.bat or: "
            "pip install 'markitdown[docx,pptx,xlsx,pdf]>=0.0.1a3'"
        ) from exc

    logger.info("Converting with MarkItDown: %s", path.name)
    md = MarkItDown(enable_plugins=False)
    result = md.convert(str(path))
    text = getattr(result, "markdown", None) or getattr(result, "text_content", None) or ""
    if not str(text).strip():
        logger.warning("MarkItDown returned empty content for %s", path.name)
    return str(text)


def convert_document(
    input_path: str | Path,
    *,
    output_dir: Optional[Path] = None,
    root: Optional[Path] = None,
    rtl_mode: str = "none",
    keep_images_separate: bool = False,
) -> Optional[Path]:
    path = Path(input_path).expanduser().resolve()
    if not path.exists():
        logger.error("File not found: %s", path)
        return None
    if not path.is_file():
        logger.error("Not a file: %s", path)
        return None

    try:
        text = _markitdown_convert(path)
        if path.suffix.lower() == ".pdf":
            text = convert_pdf_smart(path, text, rtl_mode=rtl_mode)
        else:
            text = fix_rtl_text(text, mode=rtl_mode)

        images_dir = None
        if keep_images_separate:
            out_base = output_path_for(path, output_dir=output_dir, root=root)
            images_dir = out_base.parent / "images"

        text = embed_images(
            path,
            text,
            keep_separate=keep_images_separate,
            images_dir=images_dir,
        )

        out = output_path_for(path, output_dir=output_dir, root=root)
        out.write_text(text, encoding="utf-8")
        logger.info("Wrote %s (%s)", out, human_size(out.stat().st_size))
        return out
    except Exception as exc:
        logger.error("Conversion failed for %s: %s", path.name, exc)
        logger.debug("Traceback", exc_info=True)
        return None


def convert_folder(
    folder: str | Path,
    *,
    recursive: bool = True,
    extensions: Optional[Set[str]] = None,
    output_dir: Optional[Path] = None,
    merge: bool = False,
    rtl_mode: str = "none",
    keep_images_separate: bool = False,
    show_progress: bool = True,
) -> List[Path]:
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        logger.error("Not a directory: %s", root)
        return []

    allowed = extensions if extensions is not None else SUPPORTED_DOC_EXTENSIONS
    pattern = "**/*" if recursive else "*"
    candidates = [
        p
        for p in sorted(root.glob(pattern))
        if p.is_file() and p.suffix.lower() in allowed and p.suffix.lower() != ".md"
    ]
    if not candidates:
        logger.warning("No matching documents in %s", root)
        return []

    logger.info("Found %d document(s) in %s", len(candidates), root)
    written: List[Path] = []
    failed: List[str] = []
    t0 = time.perf_counter()

    iterator = candidates
    try:
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(candidates, desc="Converting", unit="file")
    except ImportError:
        pass

    for path in iterator:
        out = convert_document(
            path,
            output_dir=output_dir,
            root=root,
            rtl_mode=rtl_mode,
            keep_images_separate=keep_images_separate,
        )
        if out is not None:
            written.append(out)
        else:
            failed.append(path.name)

    elapsed = time.perf_counter() - t0
    logger.info(
        "Folder done: %d/%d succeeded in %.1fs",
        len(written),
        len(candidates),
        elapsed,
    )
    if failed:
        logger.warning("Failed: %s", ", ".join(failed))

    if merge and written:
        merge_path = _merge_outputs(written, root, output_dir)
        if merge_path:
            logger.info("Merged output: %s", merge_path)
            return [merge_path]

    return written


def _merge_outputs(
    paths: List[Path],
    root: Path,
    output_dir: Optional[Path],
) -> Optional[Path]:
    lines = [f"# Merged conversion of `{root.name}`\n", "## Table of contents\n"]
    for i, p in enumerate(paths, 1):
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            rel = p.name
        anchor = rel.replace("/", "-").replace(".", "")
        lines.append(f"{i}. [{rel}](#{anchor})")

    lines.append("")
    for p in paths:
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            rel = p.name
        anchor = rel.replace("/", "-").replace(".", "")
        body = p.read_text(encoding="utf-8", errors="replace")
        lines.append(f"\n---\n\n## {rel} {{#{anchor}}}\n\n{body.rstrip()}\n")

    content = "\n".join(lines)
    if output_dir:
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / f"{root.name}_merged.md"
    else:
        out = root / f"{root.name}_merged.md"
    out.write_text(content, encoding="utf-8")
    return out


__all__ = [
    "convert_document",
    "convert_folder",
    "parse_extensions",
    "SUPPORTED_DOC_EXTENSIONS",
]
