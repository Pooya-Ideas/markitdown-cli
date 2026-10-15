# Markitdown-CLI

**Convert Word, PowerPoint, Excel, PDF — and entire code projects — into self-contained Markdown optimized for LLMs.**

Windows-friendly CLI + GUI around [Microsoft MarkItDown](https://github.com/microsoft/markitdown), with image embedding, smarter Persian/Arabic PDF handling, and a **code-project packer** for ChatGPT / Claude / Grok.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Pooya-Ideas/markitdown-cli/actions/workflows/python-package.yml/badge.svg)](https://github.com/Pooya-Ideas/markitdown-cli/actions/workflows/python-package.yml)

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

---

## Documentation

- **[Docs home](docs/Home.md)** — full guide
- [Installation](docs/Installation.md) · [Usage](docs/Usage.md) · [Persian PDF](docs/Persian-PDF.md) · [Troubleshooting](docs/Troubleshooting.md)
- [Code of Conduct](CODE_OF_CONDUCT.md) · [Security](SECURITY.md) · [Accessibility](ACCESSIBILITY.md) · [Contributing](CONTRIBUTING.md)

---

## Farsi / Persian PDF notes

- Default RTL mode keeps **logical** Unicode order (correct for LLMs).
- Structural cleanup fixes section numbers, mid-word line breaks, and compound hyphens.
- Broken PDF font maps still need DOCX source or OCR — see [Persian-PDF](docs/Persian-PDF.md).

---

## License

MIT — see [LICENSE](LICENSE).
