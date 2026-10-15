"""CLI --check smoke test."""

from doc2md.checks import format_checks_text, run_checks


def test_run_checks_returns_python():
    results = run_checks()
    names = {r.name for r in results}
    assert "python" in names
    assert "markitdown" in names


def test_format_text_nonempty():
    text = format_checks_text()
    assert "Python" in text or "python" in text
