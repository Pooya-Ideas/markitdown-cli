"""Command-line interface for Markitdown-CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from doc2md import __version__
from doc2md.checks import format_checks_json, format_checks_text
from doc2md.code_project import convert_code_project
from doc2md.core import convert_document, convert_folder
from doc2md.rtl import resolve_rtl_mode
from doc2md.utils import ensure_utf8_stdio, parse_extensions, setup_logging


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="doc2md",
        description=(
            "Markitdown-CLI — convert Office/PDF documents and code projects "
            "to self-contained Markdown optimized for LLMs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  doc2md report.docx
  doc2md --folder ./docs --ext pdf,docx
  doc2md --folder ./docs --merge --output-dir ./out
  doc2md --code-project ./my-app --single-file
  doc2md --check
  doc2md --stdin --format html < page.html > page.md
""",
    )
    p.add_argument("input", nargs="?", help="Input file path")
    p.add_argument("--folder", "-f", metavar="DIR", help="Convert documents in folder")
    p.add_argument("--ext", metavar="LIST", help="Comma-separated extensions (e.g. docx,pdf)")
    p.add_argument("--no-recursive", action="store_true", help="Do not scan subfolders")
    p.add_argument("--merge", action="store_true", help="Merge folder outputs into one Markdown")
    p.add_argument("--output-dir", "-o", metavar="DIR", help="Write outputs under this directory")
    p.add_argument("--keep-images-separate", action="store_true", help="Save images under images/ instead of Base64")
    p.add_argument("--rtl-visual", action="store_true", help="Apply visual RTL reordering (NOT recommended for LLM Markdown)")
    p.add_argument("--no-rtl-fix", action="store_true", help="Disable all RTL post-processing (default behaviour)")
    p.add_argument("--rtl-mode", choices=["none", "marks", "visual"], help="RTL handling: none (default), marks, or visual")
    p.add_argument("--code-project", metavar="DIR", help="Convert a source-code tree to Markdown")
    p.add_argument("--single-file", action="store_true", default=True, help="Code project: one merged Markdown (default)")
    p.add_argument("--per-file", action="store_true", help="Code project: one .md per source file")
    p.add_argument("--include", action="append", default=[], help="Code project: path must contain this")
    p.add_argument("--exclude", action="append", default=[], help="Code project: skip paths containing this")
    p.add_argument("--max-file-size", type=int, default=1_000_000, help="Code project: skip files larger than this many bytes")
    p.add_argument("--check", action="store_true", help="Print dependency status and exit")
    p.add_argument("--check-json", action="store_true", help="Print dependency status as JSON")
    p.add_argument("--stdin", action="store_true", help="Read document bytes from stdin")
    p.add_argument("--format", metavar="EXT", help="Hint for --stdin (e.g. docx, pdf, html)")
    p.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    p.add_argument("--quiet", "-q", action="store_true", help="Warnings and errors only")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _convert_stdin(fmt: Optional[str], rtl_mode: str) -> int:
    import tempfile
    data = sys.stdin.buffer.read()
    if not data:
        print("[ERROR] stdin is empty", file=sys.stderr)
        return 1
    ext = (fmt or "txt").lstrip(".")
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    out = None
    try:
        out = convert_document(tmp_path, rtl_mode=rtl_mode)
        if out is None:
            return 1
        sys.stdout.write(out.read_text(encoding="utf-8"))
        return 0
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
            if out and out.exists() and out != tmp_path:
                out.unlink(missing_ok=True)
        except Exception:
            pass


def main(argv: Optional[list] = None) -> int:
    ensure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(verbose=args.verbose, quiet=args.quiet)

    if args.check or args.check_json:
        print(format_checks_json() if args.check_json else format_checks_text())
        return 0

    rtl_mode = resolve_rtl_mode(
        rtl_visual=args.rtl_visual,
        no_rtl_fix=args.no_rtl_fix,
        rtl_mode=args.rtl_mode,
    )
    output_dir = Path(args.output_dir) if args.output_dir else None

    if args.stdin:
        return _convert_stdin(args.format, rtl_mode)

    if args.code_project:
        single = not args.per_file
        try:
            written = convert_code_project(
                Path(args.code_project),
                include=args.include or None,
                exclude=args.exclude or None,
                max_file_size=args.max_file_size,
                single_file=single,
                output_dir=output_dir,
            )
        except Exception as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 1
        return 0 if written else 1

    if args.folder:
        exts = parse_extensions(args.ext)
        written = convert_folder(
            args.folder,
            recursive=not args.no_recursive,
            extensions=exts,
            output_dir=output_dir,
            merge=args.merge,
            rtl_mode=rtl_mode,
            keep_images_separate=args.keep_images_separate,
            show_progress=not args.quiet,
        )
        return 0 if written else 1

    if not args.input:
        parser.print_help()
        return 1

    out = convert_document(
        args.input,
        output_dir=output_dir,
        rtl_mode=rtl_mode,
        keep_images_separate=args.keep_images_separate,
    )
    return 0 if out is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
