#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backward-compatible entry point.

    python converter.py file.docx
    python converter.py --folder ./docs
    python converter.py --check

Delegates to the doc2md package (v2).
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from doc2md.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
