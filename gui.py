#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markitdown CLI — Simple GUI
A lightweight Tkinter interface for converting documents to Markdown.
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from converter import convert_file, convert_folder, parse_extensions, SUPPORTED_EXTENSIONS
except ImportError as e:
    print(f"Failed to import converter: {e}")
    print("Make sure converter.py is in the same folder as gui.py")
    sys.exit(1)


class MarkitdownGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Markitdown CLI")
        self.geometry("720x520")
        self.minsize(560, 400)

        self.mode = tk.StringVar(value="file")
        self.path_var = tk.StringVar()
        self.ext_var = tk.StringVar(value="all")
        self.busy = False

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        title = ttk.Label(self, text="Markitdown CLI", font=("Segoe UI", 16, "bold"))
        title.pack(pady=(14, 4))
        subtitle = ttk.Label(
            self,
            text="Convert Word, PowerPoint, Excel, PDF → self-contained Markdown",
            font=("Segoe UI", 9),
        )
        subtitle.pack(pady=(0, 10))

        mode_frame = ttk.LabelFrame(self, text="Mode", padding=8)
        mode_frame.pack(fill="x", **pad)
        ttk.Radiobutton(
            mode_frame, text="Single file", variable=self.mode, value="file",
            command=self._on_mode_change
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            mode_frame, text="Whole folder", variable=self.mode, value="folder",
            command=self._on_mode_change
        ).pack(side="left", padx=8)

        path_frame = ttk.LabelFrame(self, text="Path", padding=8)
        path_frame.pack(fill="x", **pad)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.browse_btn = ttk.Button(path_frame, text="Browse…", command=self._browse)
        self.browse_btn.pack(side="right")

        self.fmt_frame = ttk.LabelFrame(self, text="Formats (folder mode)", padding=8)
        self.fmt_frame.pack(fill="x", **pad)
        formats = [
            ("All supported", "all"),
            ("Word (.docx)", "docx"),
            ("PowerPoint (.pptx)", "pptx"),
            ("Excel (.xlsx / .xls)", "xlsx,xls"),
            ("PDF (.pdf)", "pdf"),
        ]
        for text, val in formats:
            ttk.Radiobutton(
                self.fmt_frame, text=text, variable=self.ext_var, value=val
            ).pack(anchor="w")

        self.convert_btn = ttk.Button(self, text="Convert", command=self._start_convert)
        self.convert_btn.pack(pady=10)

        log_frame = ttk.LabelFrame(self, text="Log", padding=6)
        log_frame.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(log_frame, height=12, wrap="word", font=("Consolas", 9))
        self.log.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        scroll.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scroll.set)

        self._on_mode_change()
        self._log("Ready. Select a file or folder and click Convert.")

    def _on_mode_change(self) -> None:
        if self.mode.get() == "folder":
            self.fmt_frame.pack(fill="x", padx=10, pady=6)
        else:
            self.fmt_frame.pack_forget()

    def _browse(self) -> None:
        if self.mode.get() == "file":
            path = filedialog.askopenfilename(
                title="Select document",
                filetypes=[
                    ("Documents", "*.docx *.pptx *.xlsx *.xls *.pdf *.html *.htm *.csv *.txt *.md"),
                    ("All files", "*.*"),
                ],
            )
        else:
            path = filedialog.askdirectory(title="Select folder")
        if path:
            self.path_var.set(path)

    def _log(self, msg: str) -> None:
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.convert_btn.configure(state=state)
        self.browse_btn.configure(state=state)

    def _start_convert(self) -> None:
        if self.busy:
            return
        path = self.path_var.get().strip().strip('"').strip("'")
        if not path:
            messagebox.showwarning("No path", "Please select a file or folder first.")
            return
        p = Path(path)
        if not p.exists():
            messagebox.showerror("Not found", f"Path does not exist:\n{path}")
            return

        self._set_busy(True)
        self._log("")
        self._log(f"Starting… ({path})")

        def worker() -> None:
            try:
                class LogWriter:
                    def __init__(self, app: MarkitdownGUI) -> None:
                        self.app = app

                    def write(self, s: str) -> None:
                        if s and s.strip():
                            self.app.after(0, lambda m=s.rstrip(): self.app._log(m))

                    def flush(self) -> None:
                        pass

                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout = sys.stderr = LogWriter(self)
                try:
                    if self.mode.get() == "file":
                        result = convert_file(path)
                        ok = result is not None
                    else:
                        exts = parse_extensions(self.ext_var.get())
                        count = convert_folder(path, recursive=True, extensions=exts)
                        ok = count > 0
                finally:
                    sys.stdout, sys.stderr = old_stdout, old_stderr

                def done() -> None:
                    self._set_busy(False)
                    if ok:
                        self._log("Done.")
                        messagebox.showinfo("Success", "Conversion finished.")
                    else:
                        self._log("Finished with errors.")
                        messagebox.showwarning("Finished", "Conversion finished with errors. Check the log.")

                self.after(0, done)
            except Exception as e:
                def fail() -> None:
                    self._set_busy(False)
                    self._log(f"Error: {e}")
                    messagebox.showerror("Error", str(e))

                self.after(0, fail)

        threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    app = MarkitdownGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
