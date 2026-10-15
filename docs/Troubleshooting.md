# Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Python was not found` | Install Python 3.10+ and check “Add to PATH” |
| `markitdown not installed` | Run `install.bat` or `pip install -e .` |
| Batch window closes | Use `run.bat` (includes pause); ensure UTF-8 (`chcp 65001`) |
| Persian PDF looks wrong | See [Persian-PDF](Persian-PDF); try DOCX source |
| GUI won’t start | `python gui.py` from a terminal to see the error |
| Permission errors on pip | `python -m pip install --user -e .` |
