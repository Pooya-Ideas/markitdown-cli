# Contributing

Thanks for your interest!

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep backward compatibility for `python converter.py <file>`.
- Do **not** apply visual RTL reordering to saved Markdown by default.
- Add tests for new behaviour under `tests/`.
- Run `flake8 doc2md tests` before opening a PR.
- User-facing docs in English; community translations welcome.

## Reporting issues

Include OS, Python version, `python converter.py --check` output, and a minimal sample file when possible.

See also: [[Code-of-Conduct]], [[Security]], [[Accessibility]].
