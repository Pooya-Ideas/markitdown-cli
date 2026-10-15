"""Code project mode tests."""

from pathlib import Path

from doc2md.code_project import collect_code_files, convert_code_project

FIXTURE = Path(__file__).parent / "fixtures" / "sample_code_project"


def test_ignores_node_modules():
    files = collect_code_files(FIXTURE)
    names = {f.name for f in files}
    assert "main.py" in names
    assert "utils.js" in names
    assert "ignore.js" not in names


def test_convert_merged(tmp_path):
    outs = convert_code_project(FIXTURE, single_file=True, output_dir=tmp_path)
    assert len(outs) == 1
    text = outs[0].read_text(encoding="utf-8")
    assert "main.py" in text
    assert "```python" in text
    assert "ignore.js" not in text
