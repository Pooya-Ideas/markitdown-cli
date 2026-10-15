# Architecture

```
markitdown-cli/
├── converter.py          # thin CLI entry (backward compatible)
├── gui.py                # Tkinter UI
├── doc2md/
│   ├── cli.py            # argparse interface
│   ├── core.py           # document / folder conversion
│   ├── pdf.py            # PDF quality + Farsi cleanup
│   ├── rtl.py            # RTL modes (default: none)
│   ├── images.py         # undoc Base64 embedding
│   ├── code_project.py   # source tree → Markdown
│   ├── checks.py         # dependency probe
│   └── utils.py
├── tests/
└── .github/workflows/
```

**Pipeline:** MarkItDown text → PDF smart path (optional) → image embed → write `.md`.
