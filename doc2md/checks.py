"""Dependency checks — single source of truth for check.bat and CLI."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    required: bool = True


def _py_version() -> CheckResult:
    v = sys.version_info
    ok = v >= (3, 10)
    return CheckResult(
        name="python",
        ok=ok,
        detail=f"{v.major}.{v.minor}.{v.micro}",
        required=True,
    )


def _pkg(name: str, import_name: str | None = None, required: bool = True) -> CheckResult:
    mod = import_name or name
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", "installed")
        return CheckResult(name=name, ok=True, detail=str(ver), required=required)
    except ImportError:
        if name == "pymupdf":
            try:
                m = __import__("fitz")
                ver = getattr(m, "__version__", "installed(fitz)")
                return CheckResult(name=name, ok=True, detail=str(ver), required=required)
            except ImportError:
                pass
        return CheckResult(name=name, ok=False, detail="not installed", required=required)


def run_checks() -> List[CheckResult]:
    results = [
        _py_version(),
        _pkg("markitdown", required=True),
        _pkg("undoc", required=False),
        _pkg("pymupdf", import_name="pymupdf", required=False),
        _pkg("python-bidi", import_name="bidi", required=False),
    ]
    return results


def checks_as_dict() -> Dict[str, Any]:
    rows = run_checks()
    return {
        "ok": all(r.ok for r in rows if r.required),
        "checks": [asdict(r) for r in rows],
    }


def format_checks_text(results: List[CheckResult] | None = None) -> str:
    results = results or run_checks()
    lines = ["Markitdown-CLI — dependency check", "-" * 40]
    for r in results:
        flag = "OK" if r.ok else "MISSING"
        req = "required" if r.required else "optional"
        lines.append(f"  [{flag}] {r.name}: {r.detail} ({req})")
    lines.append("-" * 40)
    if all(r.ok for r in results if r.required):
        lines.append("All required dependencies are present.")
    else:
        lines.append("Some required dependencies are missing. Run install.bat")
    return "\n".join(lines)


def format_checks_json(results: List[CheckResult] | None = None) -> str:
    results = results or run_checks()
    return json.dumps(checks_as_dict(), indent=2, ensure_ascii=False)
