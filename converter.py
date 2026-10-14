#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markitdown CLI Converter
========================
Converts Office documents (DOCX, PPTX, XLSX), PDF and other formats
supported by MarkItDown into self-contained Markdown files
with images embedded as Base64 data URIs.

Supports single-file mode and whole-folder mode (with format filter).
Special handling for Persian/Arabic (RTL) PDFs.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Set

SUPPORTED_EXTENSIONS = {
    ".docx", ".pptx", ".xlsx", ".xls",
    ".pdf",
    ".html", ".htm",
    ".csv", ".json", ".xml",
    ".txt", ".md",
    ".epub",
    ".msg",
}

PERSIAN_ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")


def warn(msg: str) -> None:
    print(f"[WARNING] {msg}")


def error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def check_markitdown() -> bool:
    try:
        from markitdown import MarkItDown  # noqa: F401
        return True
    except ImportError:
        return False


def check_undoc() -> bool:
    try:
        from undoc import parse_file  # noqa: F401
        return True
    except ImportError:
        return False


def check_pymupdf() -> bool:
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        return False


def check_bidi() -> bool:
    try:
        from bidi.algorithm import get_display  # noqa: F401
        return True
    except ImportError:
        return False


def contains_persian_or_arabic(text: str) -> bool:
    return bool(PERSIAN_ARABIC_RE.search(text))


def fix_rtl_text(text: str) -> str:
    if not check_bidi():
        return text
    try:
        from bidi.algorithm import get_display
        lines = text.splitlines()
        fixed = []
        for line in lines:
            if contains_persian_or_arabic(line):
                fixed.append(get_display(line))
            else:
                fixed.append(line)
        return "\n".join(fixed)
    except Exception as exc:
        warn(f"RTL fix failed: {exc}")
        return text


def convert_pdf_with_pymupdf(input_path: Path) -> Optional[str]:
    if not check_pymupdf():
        return None
    try:
        import fitz
        doc = fitz.open(str(input_path))
        pages = [page.get_text("text") for page in doc]
        doc.close()
        return "\n\n".join(pages)
    except Exception as exc:
        warn(f"PyMuPDF extraction failed: {exc}")
        return None


def convert_with_markitdown(input_path: Path) -> str:
    from markitdown import MarkItDown

    info("Step 1: Converting text, headings, lists and tables with MarkItDown...")
    md = MarkItDown(enable_plugins=False)
    result = md.convert(str(input_path))
    markdown = getattr(result, "markdown", None) or getattr(result, "text_content", None) or ""
    if not markdown.strip():
        warn("MarkItDown returned empty content. The file may be image-only or corrupted.")
    return markdown


def convert_pdf_smart(input_path: Path) -> str:
    markdown = convert_with_markitdown(input_path)
    has_fa = contains_persian_or_arabic(markdown)

    if has_fa:
        info("Persian/Arabic text detected – applying RTL fixes...")
        if check_pymupdf():
            alt = convert_pdf_with_pymupdf(input_path)
            if alt and contains_persian_or_arabic(alt):
                def single_char_ratio(t: str) -> float:
                    words = t.split()
                    if not words:
                        return 1.0
                    return sum(1 for w in words if len(w) == 1) / len(words)

                if single_char_ratio(alt) < single_char_ratio(markdown):
                    info("Using PyMuPDF extraction (better RTL character order).")
                    markdown = alt
                else:
                    info("Keeping MarkItDown result.")
        else:
            warn("PyMuPDF not installed – for better Persian PDF results run: "
                 "pip install pymupdf python-bidi")
        markdown = fix_rtl_text(markdown)

    return markdown


def extract_and_embed_images(input_path: Path, markdown: str) -> str:
    if not check_undoc():
        warn("undoc is not installed – skipping image extraction.")
        return markdown

    suffix = input_path.suffix.lower()
    if suffix not in {".docx", ".pptx", ".xlsx"}:
        info("Image extraction only available for .docx / .pptx / .xlsx. Skipping.")
        return markdown

    try:
        from undoc import parse_file
    except ImportError:
        warn("Could not import undoc – skipping image extraction.")
        return markdown

    info("Step 2: Extracting embedded images with undoc...")

    try:
        doc = parse_file(str(input_path))
    except Exception as exc:
        warn(f"undoc failed to parse the file: {exc}")
        return markdown

    try:
        resource_ids = doc.get_resource_ids()
    except AttributeError:
        resource_ids = getattr(doc, "resources", {})
        if isinstance(resource_ids, dict):
            resource_ids = list(resource_ids.keys())
        else:
            resource_ids = []

    if not resource_ids:
        info("No embedded resources found.")
        return markdown

    image_blocks: List[str] = []
    embedded_count = 0

    for rid in resource_ids:
        try:
            info_dict = doc.get_resource_info(rid)
            role = info_dict.get("role", "primary")
            if isinstance(role, str) and role.lower() != "primary":
                continue

            mime = info_dict.get("mime_type") or info_dict.get("content_type") or "image/png"
            filename = info_dict.get("filename") or f"image_{rid}"
            data = doc.get_resource_data(rid)
            if not data:
                continue

            if mime == "application/octet-stream" or not str(mime).startswith("image/"):
                guessed, _ = mimetypes.guess_type(filename)
                mime = guessed if guessed and guessed.startswith("image/") else "image/png"

            b64 = base64.b64encode(data).decode("ascii")
            alt = Path(filename).stem or f"image_{embedded_count + 1}"
            image_blocks.append(f"![{alt}](data:{mime};base64,{b64})")
            embedded_count += 1
        except Exception as exc:
            warn(f"Could not extract resource {rid}: {exc}")
            continue

    if embedded_count == 0:
        info("No primary images could be extracted.")
        return markdown

    info(f"Embedded {embedded_count} image(s) as Base64 data URIs.")
    footer = "\n\n---\n\n## Extracted Images\n\n" + "\n\n".join(image_blocks)
    return markdown.rstrip() + footer


def convert_file(input_path: str | Path) -> Optional[Path]:
    input_path = Path(input_path).expanduser().resolve()

    if not input_path.exists():
        error(f"File not found: {input_path}")
        return None
    if not input_path.is_file():
        error(f"Path is not a file: {input_path}")
        return None
    if not check_markitdown():
        error("markitdown is not installed. Run install.bat first.")
        return None

    output_path = input_path.with_suffix(".md")

    try:
        if input_path.suffix.lower() == ".pdf":
            markdown = convert_pdf_smart(input_path)
        else:
            markdown = convert_with_markitdown(input_path)

        markdown = extract_and_embed_images(input_path, markdown)

        info(f"Writing output → {output_path}")
        output_path.write_text(markdown, encoding="utf-8")

        size_kb = output_path.stat().st_size / 1024
        success("Conversion complete!")
        print(f"         Output : {output_path}")
        print(f"         Size   : {size_kb:.1f} KB")
        return output_path

    except Exception as exc:
        error(f"Conversion failed: {exc}")
        traceback.print_exc(limit=3)
        return None


def parse_extensions(ext_arg: Optional[str]) -> Optional[Set[str]]:
    if not ext_arg or ext_arg.strip().lower() in {"all", "*"}:
        return None
    result = set()
    for part in ext_arg.split(","):
        part = part.strip().lower().lstrip(".")
        if part:
            result.add("." + part)
    return result if result else None


def convert_folder(
    folder_path: str | Path,
    recursive: bool = True,
    extensions: Optional[Set[str]] = None,
) -> int:
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists():
        error(f"Folder not found: {folder}")
        return 0
    if not folder.is_dir():
        error(f"Path is not a folder: {folder}")
        return 0
    if not check_markitdown():
        error("markitdown is not installed. Run install.bat first.")
        return 0

    allowed = extensions if extensions is not None else SUPPORTED_EXTENSIONS
    pattern = "**/*" if recursive else "*"

    candidates = [
        p for p in folder.glob(pattern)
        if p.is_file()
        and p.suffix.lower() in allowed
        and p.suffix.lower() != ".md"
    ]

    if not candidates:
        warn(f"No matching files found in: {folder}")
        if extensions:
            warn(f"Looking for extensions: {', '.join(sorted(extensions))}")
        return 0

    info(f"Found {len(candidates)} matching file(s) in: {folder}")
    print()

    success_count = 0
    for i, file_path in enumerate(candidates, 1):
        print(f"---------- [{i}/{len(candidates)}] {file_path.name} ----------")
        result = convert_file(file_path)
        if result is not None:
            success_count += 1
        print()

    print("=" * 50)
    success(f"Folder done: {success_count}/{len(candidates)} file(s) converted.")
    return success_count


def main() -> int:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Markitdown CLI – Convert Office / PDF documents to self-contained Markdown"
    )
    parser.add_argument("input", nargs="?", help="Path to a single input file")
    parser.add_argument("--folder", "-f", metavar="DIR", help="Convert all matching files inside this folder")
    parser.add_argument(
        "--ext",
        metavar="LIST",
        help="Comma-separated extensions to convert, e.g. docx,pdf,pptx (default: all supported)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="When using --folder, do not scan sub-folders",
    )
    args = parser.parse_args()

    if args.folder:
        exts = parse_extensions(args.ext)
        count = convert_folder(args.folder, recursive=not args.no_recursive, extensions=exts)
        return 0 if count > 0 else 1

    if not args.input:
        print("Markitdown CLI Converter")
        print("------------------------")
        try:
            path = input("Enter full path to the file: ").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        if not path:
            error("No path provided.")
            return 1
        args.input = path

    result = convert_file(args.input)
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
