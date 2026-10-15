# Contributing to Markitdown-CLI

Thanks for your interest!

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep backward compatibility for `python converter.py <file>`.
- Do not apply visual RTL reordering to saved Markdown by default.
- Add tests for new behaviour under `tests/`.
- Run `flake8 doc2md tests` before opening a PR.
- User-facing docs in README; code comments/docstrings in English.

## Reporting issues

Include OS, Python version, `doc2md --check` output, and a minimal sample file when possible.
