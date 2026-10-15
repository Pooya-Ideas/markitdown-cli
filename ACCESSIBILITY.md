# Accessibility

## Commitment

Markitdown-CLI aims to be usable by as many people as possible. We prioritize:

- Clear, plain-language documentation (English; community translations welcome)
- Keyboard-friendly CLI and GUI flows where the platform allows
- Text-first outputs (Markdown) that work with screen readers and assistive tech
- Avoiding reliance on color alone for success/error state in CLI messages

## Supported environments

| Surface | Accessibility notes |
|--------|---------------------|
| **CLI** (`converter.py` / `doc2md`) | Fully keyboard-driven. Works with Windows Terminal, PowerShell, cmd, and common Linux terminals. UTF-8 / RTL text is supported when the console is set to UTF-8 (`chcp 65001` on Windows). |
| **GUI** (`gui.py`) | Built with Tkinter. Basic keyboard navigation depends on the OS/Tk theme. Screen-reader support is **limited** (Tkinter is not a full AT-accessible toolkit). |
| **Markdown output** | Logical Unicode order is preserved by default (important for Persian/Arabic). Base64 images are embedded as Markdown image syntax. |
| **Windows batch menus** | Numbered menus are operable with keyboard only. |

## Known limitations

1. **Tkinter GUI** — Not WCAG-conformant. Prefer the CLI if you rely on screen readers.
2. **Persian/Arabic PDF extraction** — Some PDFs have broken font maps; text may be incomplete. Prefer `.docx` sources when possible.
3. **Color in terminals** — Success/error messages may use color when available; status is also written in plain text (`[OK]`, `[ERROR]`).
4. **High-contrast / large text** — CLI inherits terminal settings; GUI font scaling follows OS Tk defaults and may be limited.

## Reporting accessibility barriers

Please open a GitHub issue with the **Accessibility barrier** template, or email the maintainer via the profile contact.

Helpful details:

- Assistive technology and OS version
- Steps to reproduce the barrier
- What you expected vs what happened
- Severity (blocker / major / minor)

We treat accessibility reports with the same priority as functional bugs.
