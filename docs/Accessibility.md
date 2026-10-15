# Accessibility

## Commitment

Markitdown-CLI prioritizes clear documentation, keyboard-friendly CLI use, and text-first Markdown outputs that work with assistive technology.

## Supported environments

| Surface | Notes |
|---------|--------|
| CLI | Fully keyboard-driven; UTF-8 / RTL when the terminal is UTF-8 |
| GUI (Tkinter) | Limited screen-reader support — prefer CLI if you rely on AT |
| Markdown output | Logical Unicode order by default; good for screen readers |

## Known limitations

- Tkinter GUI is not WCAG-conformant.
- Some Persian PDFs have broken font maps (prefer DOCX or OCR).
- Terminal colors are optional; status is also plain text (`[OK]` / `[ERROR]`).

## Report a barrier

Open an issue with the **Accessibility barrier** template.

Full page: [ACCESSIBILITY.md](https://github.com/Pooya-Ideas/markitdown-cli/blob/main/ACCESSIBILITY.md).
