# Changelog

## 2.0.1 — 2026-10-15

### Fixed
- PDF structural cleanup for Farsi academic documents:
  - Section numbers split across lines (`1` / `-` / `1` → `1-1`)
  - Mid-word newlines and missing spaces at line wraps
  - Compound hyphen breaks (`بی - توجهی` → `بی‌توجهی`)
  - Prefer PyMuPDF block extraction for reading order
  - Warn when PDF font-map artifacts (extra letters) are dense — prefer DOCX/OCR
- `install.bat` rewritten with CRLF and one-line pip installs (Windows cmd compatibility)
- GUI import SyntaxError and output-directory field
- `check.bat` uses `converter.py --check` only

## 2.0.0 — 2026-10-14

### Fixed
- Disabled default visual RTL reordering (`python-bidi.get_display`) which corrupted logical order in Markdown files.
- Replaced naive `single_char_ratio` PDF heuristic with composite `pdf_quality_score`.
- Made `undoc` API usage explicit; raise clear errors on API mismatch instead of silent fallbacks.
- Pinned dependency version ranges in `install.bat` and `pyproject.toml`.
- Attempt in-place Base64 image embedding before appending at end of file.
- Unified dependency checks via `converter.py --check` (single source of truth).

### Added
- Package layout under `doc2md/` with modular modules (`core`, `pdf`, `rtl`, `images`, `code_project`, `cli`).
- Code-project mode (`--code-project`) for packing source trees into LLM-friendly Markdown.
- Folder `--merge` mode with table of contents.
- `--output-dir`, `--keep-images-separate`, `--rtl-visual`, `--no-rtl-fix`, `--verbose`, `--quiet`.
- stdin/stdout pipeline support (`--stdin --format ...`).
- `pyproject.toml` with console entry points `doc2md` and `markitdown-cli`.
- pytest suite under `tests/`.
- Progress bar (tqdm) for folder conversion when available.

### Compatibility
- `python converter.py file.docx` still works.
- GUI (`gui.py` / `gui.bat`) retained.
