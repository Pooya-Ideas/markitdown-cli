# Usage

## Interactive menu

Double-click `run.bat` (Windows).

## Single file

```bat
python converter.py "C:\path\to\file.docx"
python converter.py report.pdf --output-dir .\out
```

## Folder

```bat
python converter.py --folder .\docs --ext pdf,docx
python converter.py --folder .\docs --merge
```

## Code project (for LLMs)

```bat
python converter.py --code-project .\my-app --single-file
```

Produces a single Markdown with tree + fenced source blocks.

## GUI

```bat
gui.bat
```

## Stdin pipeline

```bash
cat page.html | python converter.py --stdin --format html > page.md
```
