"""Image extraction and embedding for Office documents."""

from __future__ import annotations

import base64
import logging
import mimetypes
import re
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger("doc2md.images")

_PLACEHOLDER_RE = re.compile(
    r"(!\[([^\]]*)\]\(([^)]+)\))"
    r"|(\[image\d*\])"
    r"|(!\[image\])",
    re.IGNORECASE,
)

UNDO_API_METHODS = ("get_resource_ids", "get_resource_info", "get_resource_data")


def _extract_resources(path: Path) -> List[Tuple[str, str, bytes]]:
    try:
        from undoc import parse_file
    except ImportError as exc:
        raise RuntimeError(
            "undoc is not installed. Run install.bat or: pip install 'undoc>=0.1.0'"
        ) from exc

    try:
        doc = parse_file(str(path))
    except Exception as exc:
        raise RuntimeError(f"undoc failed to parse {path.name}: {exc}") from exc

    for method in UNDO_API_METHODS:
        if not hasattr(doc, method):
            raise RuntimeError(
                f"undoc API mismatch: Document has no '{method}'. "
                "Pin a compatible undoc version (see install.bat / pyproject.toml)."
            )

    resource_ids = doc.get_resource_ids()
    if not resource_ids:
        return []

    results: List[Tuple[str, str, bytes]] = []
    for rid in resource_ids:
        try:
            info = doc.get_resource_info(rid)
            role = str(info.get("role", "primary")).lower()
            if role != "primary":
                continue
            mime = info.get("mime_type") or info.get("content_type") or "image/png"
            filename = info.get("filename") or f"image_{rid}"
            data = doc.get_resource_data(rid)
            if not data:
                continue
            if not str(mime).startswith("image/"):
                guessed, _ = mimetypes.guess_type(str(filename))
                mime = guessed if guessed and guessed.startswith("image/") else "image/png"
            results.append((str(filename), str(mime), bytes(data)))
        except Exception as exc:
            logger.warning("Could not extract resource %s: %s", rid, exc)
    return results


def embed_images(
    path: Path,
    markdown: str,
    *,
    keep_separate: bool = False,
    images_dir: Optional[Path] = None,
) -> str:
    suffix = path.suffix.lower()
    if suffix not in {".docx", ".pptx", ".xlsx"}:
        logger.debug("Skipping image extraction for %s", suffix)
        return markdown

    try:
        resources = _extract_resources(path)
    except RuntimeError as exc:
        logger.warning("%s", exc)
        return markdown

    if not resources:
        logger.info("No primary images found in %s", path.name)
        return markdown

    logger.info("Extracted %d image(s) from %s", len(resources), path.name)

    data_uris: List[str] = []

    if keep_separate:
        out_dir = images_dir or (path.parent / "images")
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, (filename, mime, data) in enumerate(resources):
            safe = Path(filename).name or f"image_{i + 1}.png"
            dest = out_dir / safe
            if dest.exists():
                dest = out_dir / f"{dest.stem}_{i}{dest.suffix}"
            dest.write_bytes(data)
            try:
                rel = dest.relative_to(path.parent)
            except ValueError:
                rel = dest
            data_uris.append(f"![{Path(safe).stem}]({str(rel).replace(chr(92), '/')})")
    else:
        for i, (filename, mime, data) in enumerate(resources):
            b64 = base64.b64encode(data).decode("ascii")
            alt = Path(filename).stem or f"image_{i + 1}"
            data_uris.append(f"![{alt}](data:{mime};base64,{b64})")

    replaced = 0
    uri_iter = iter(data_uris)

    def _repl(match: re.Match) -> str:
        nonlocal replaced
        try:
            nxt = next(uri_iter)
            replaced += 1
            return nxt
        except StopIteration:
            return match.group(0)

    new_md = _PLACEHOLDER_RE.sub(_repl, markdown)
    remaining = data_uris[replaced:]
    if remaining:
        footer = "\n\n---\n\n## Extracted Images\n\n" + "\n\n".join(remaining)
        new_md = new_md.rstrip() + footer
        if replaced:
            logger.info("Embedded %d image(s) in-place; appended %d", replaced, len(remaining))
        else:
            logger.info("Appended %d image(s) at end of document", len(remaining))
    else:
        logger.info("Embedded all %d image(s) in-place", replaced)

    return new_md
