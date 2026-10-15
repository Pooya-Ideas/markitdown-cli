"""Tests for doc2md.utils and related helpers."""

from doc2md.utils import contains_persian_or_arabic, parse_extensions
from doc2md.pdf import pdf_quality_score


def test_parse_extensions_all():
    assert parse_extensions(None) is None
    assert parse_extensions("all") is None
    assert parse_extensions("*") is None


def test_parse_extensions_list():
    assert parse_extensions("docx,pdf") == {".docx", ".pdf"}
    assert parse_extensions(".DOCX, PDF") == {".docx", ".pdf"}


def test_persian_detection():
    assert contains_persian_or_arabic("سلام دنیا")
    assert contains_persian_or_arabic("hello سلام")
    assert not contains_persian_or_arabic("hello world")


def test_pdf_quality_score_empty():
    assert pdf_quality_score("") == 0.0


def test_pdf_quality_score_persian_better_than_noise():
    good = "این یک متن فارسی با نیم\u200cفاصله است و کلمات کامل دارد."
    noise = "ا ی ن   م ت ن"
    assert pdf_quality_score(good) > pdf_quality_score(noise)


def test_pdf_section_number_join():
    from doc2md.pdf import fix_section_numbers
    assert "1-1" in fix_section_numbers("1\n-\n1\n بیان مسئله")


def test_pdf_cleanup_toc():
    from doc2md.pdf import cleanup_pdf_text
    raw = "1\n-\n1\n بیان مسئله\n1\n-\n2\n ضرورت"
    out = cleanup_pdf_text(raw)
    assert "1-1" in out
    assert "1-2" in out
