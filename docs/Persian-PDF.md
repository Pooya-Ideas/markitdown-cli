# Persian / Arabic PDF

## What works well

- DOCX with proper Unicode fonts
- PDFs with a correct text layer
- Structural cleanup: section numbers (`1-1`), mid-word wraps, compound hyphens

## Limits

Some academic PDFs embed fonts with broken ToUnicode maps (extra letters such as `ن`).  
**No pure text extractor can invent the correct characters** — use the original Word file or OCR.

## Tips

1. Prefer `.docx` over PDF when available.
2. Default RTL mode keeps **logical** order (best for LLMs).
3. Optional: `--rtl-visual` only if you need display-oriented reordering (not recommended for chatbots).
