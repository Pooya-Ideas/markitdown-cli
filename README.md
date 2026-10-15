# Markitdown-CLI

**Convert Word, PowerPoint, Excel, PDF — and entire code projects — into self-contained Markdown optimized for LLMs.**

Windows-friendly CLI + GUI around [Microsoft MarkItDown](https://github.com/microsoft/markitdown), with image embedding, smarter Persian/Arabic PDF handling, and a **code-project packer** for ChatGPT / Claude / Grok.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()

---

## Why?

Raw `.docx` / `.pdf` uploads waste tokens. Clean Markdown often uses **60–80% fewer tokens**.  
Markitdown-CLI writes **portable `.md` files** (optional Base64 images) you can drop into any chat.

---

## Install

```bat
git clone https://github.com/Pooya-Ideas/markitdown-cli.git
cd markitdown-cli
install.bat
```

Or with pip:

```bash
pip install -e .
```

---

## Quick start

| Action | Command |
|--------|---------|
| Single file | `python converter.py report.docx` |
| Folder | `python converter.py --folder ./docs --ext pdf,docx` |
| Merge folder | `python converter.py --folder ./docs --merge` |
| Code project | `python converter.py --code-project ./my-app` |
| Check deps | `python converter.py --check` |
| GUI | double-click `gui.bat` |
| Menu | double-click `run.bat` |

After `pip install -e .`:

```bash
doc2md report.docx
doc2md --code-project ./src --single-file
```

---

## Farsi / Persian PDF notes

- Default RTL mode keeps **logical** Unicode order (correct for LLMs).
- Structural cleanup fixes: section numbers (`1-1`), mid-word line breaks, compound hyphens.
- Some PDFs have broken font maps (extra letters like `ن`) — prefer the original **Word (.docx)** or OCR for those.

---

## Project layout

```
markitdown-cli/
├── converter.py          # backward-compatible entry
├── gui.py / gui.bat
├── run.bat / check.bat / install.bat
├── doc2md/               # package
├── tests/
├── pyproject.toml
└── README.md
```

---

## License

MIT — see [LICENSE](LICENSE).
