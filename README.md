# Markitdown CLI

**Convert Word, PowerPoint, Excel, PDF and more into self-contained Markdown — optimized for LLMs.**

Simple Windows CLI + GUI wrapper around [Microsoft MarkItDown](https://github.com/microsoft/markitdown), with image embedding and Persian/Arabic PDF support.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)

---

## Why?

Uploading raw `.docx` / `.pptx` / `.pdf` to ChatGPT, Claude or Gemini wastes tokens on binary parsing.  
A clean Markdown file typically uses **60–80% fewer tokens**. Markitdown CLI outputs a **single portable `.md`** with images as Base64 data URIs — drag one file into any chat.

---

## Features

- **CLI menu** (`run.bat`) and **simple GUI** (`gui.bat`)
- Single file or whole-folder conversion
- Format filter (Word only, PDF only, custom mix…)
- MarkItDown for text/tables + undoc for embedded images
- Self-contained Markdown (no separate image folder)
- Persian / Arabic paths and smarter PDF RTL handling
- One-click install of all dependencies

---

## Quick start

1. Clone or download this repo.
2. Double-click **`install.bat`** once.
3. Use either:
   - **`gui.bat`** → graphical interface (browse file/folder → Convert)
   - **`run.bat`** → text menu (includes option to open the GUI)

---

## GUI

Double-click **`gui.bat`** (or choose option 3 in `run.bat`).

- Mode: **Single file** or **Whole folder**
- Browse for path
- In folder mode: pick All / Word / PowerPoint / Excel / PDF
- Convert → progress appears in the log panel

Requires only Python’s built-in **tkinter** (included with official Windows Python installs).

---

## CLI usage

```bat
REM Single file
python converter.py "C:\Docs\report.docx"

REM Whole folder
python converter.py --folder "C:\Docs\Project"

REM Only PDF and Word
python converter.py --folder "C:\Docs\Project" --ext docx,pdf
```

---

## Project layout

```text
markitdown-cli/
├── gui.bat          ← launch the GUI
├── run.bat          ← interactive text menu
├── gui.py           ← Tkinter interface
├── converter.py     ← conversion engine
├── check.bat
├── install.bat
├── README.md
└── LICENSE
```

---

## Requirements

- Windows 10+
- Python 3.10+ (tick “Add Python to PATH” when installing)

`install.bat` installs: `markitdown[docx,pptx,xlsx,pdf]`, `undoc`, `pymupdf`, `python-bidi`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Python not found | Reinstall Python with “Add to PATH” |
| pip permission error | Run as Administrator or `pip install --user …` |
| GUI does not open | Use `python gui.py` from a terminal to see the error; ensure tkinter is installed |
| Persian PDF text broken | Run `install.bat` again for pymupdf + python-bidi |
| Window closes too fast | Prefer `gui.bat`; or always use the menu in `run.bat` |

---

## License

MIT — see [LICENSE](LICENSE).
