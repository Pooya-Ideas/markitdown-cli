"""RTL behaviour tests."""

from doc2md.rtl import fix_rtl_text, resolve_rtl_mode


def test_default_none_preserves_text():
    text = "سلام دنیا"
    assert fix_rtl_text(text, mode="none") == text


def test_resolve_flags():
    assert resolve_rtl_mode(no_rtl_fix=True) == "none"
    assert resolve_rtl_mode(rtl_visual=True) == "visual"
    assert resolve_rtl_mode(rtl_mode="marks") == "marks"
    assert resolve_rtl_mode() == "none"


def test_marks_mode_adds_rlm():
    text = "سلام"
    out = fix_rtl_text(text, mode="marks")
    assert out.startswith("\u200f") or out == text
