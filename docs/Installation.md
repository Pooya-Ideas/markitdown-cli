# Installation

## Requirements

- Python **3.10+** on `PATH`
- Windows 10/11 recommended for `.bat` helpers (Linux/macOS CLI works too)

## One-click (Windows)

```bat
git clone https://github.com/Pooya-Ideas/markitdown-cli.git
cd markitdown-cli
install.bat
```

## pip

```bash
pip install -e .
# or
pip install -e ".[dev]"
```

## Verify

```bat
python converter.py --check
# or
doc2md --check
```

All required items should show `[OK]`.
