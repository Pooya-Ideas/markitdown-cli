"""Code-project mode: pack a source tree into LLM-friendly Markdown."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional, Sequence, Set

logger = logging.getLogger("doc2md.code")

DEFAULT_CODE_EXTENSIONS: Set[str] = {
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".py", ".pyi",
    ".rs", ".go", ".java", ".c", ".cpp", ".cc", ".h", ".hpp", ".cs",
    ".rb", ".php", ".swift", ".kt", ".kts",
    ".sh", ".bash", ".zsh", ".ps1",
    ".sql",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".md", ".mdx", ".rst", ".txt",
    ".vue", ".svelte",
}

DEFAULT_IGNORE_DIRS: Set[str] = {
    "node_modules", ".git", "dist", "build", "__pycache__",
    ".venv", "venv", "target", ".next", ".nuxt", "coverage",
    ".tox", ".mypy_cache", ".pytest_cache", ".idea", ".vscode",
    "vendor", "out", "bin", "obj", ".turbo", ".cache",
}

LANG_MAP = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "tsx", ".jsx": "jsx",
    ".rs": "rust", ".go": "go", ".java": "java",
    ".c": "c", ".cpp": "cpp", ".cc": "cpp", ".h": "c", ".hpp": "cpp",
    ".cs": "csharp", ".rb": "ruby", ".php": "php",
    ".swift": "swift", ".kt": "kotlin", ".kts": "kotlin",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash", ".ps1": "powershell",
    ".sql": "sql", ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "scss", ".sass": "sass", ".less": "less",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".xml": "xml", ".md": "markdown", ".mdx": "mdx",
    ".vue": "vue", ".svelte": "svelte",
}


def _gitignore_patterns(root: Path) -> List[re.Pattern]:
    gi = root / ".gitignore"
    patterns: List[re.Pattern] = []
    if not gi.is_file():
        return patterns
    try:
        for line in gi.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            esc = re.escape(line.rstrip("/")).replace(r"\*", ".*").replace(r"\?", ".")
            if line.endswith("/"):
                esc = esc + r"(/.*)?"
            patterns.append(re.compile(esc))
    except OSError as exc:
        logger.warning("Could not read .gitignore: %s", exc)
    return patterns


def _is_ignored(
    path: Path,
    root: Path,
    git_pats: Sequence[re.Pattern],
    extra_exclude: Sequence[str],
) -> bool:
    rel = path.relative_to(root).as_posix()
    for p in path.relative_to(root).parts:
        if p in DEFAULT_IGNORE_DIRS:
            return True
    for pattern in extra_exclude:
        if pattern and pattern in rel:
            return True
    for pat in git_pats:
        if pat.search(rel):
            return True
    return False


def collect_code_files(
    root: Path,
    *,
    include_ext: Optional[Set[str]] = None,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    max_file_size: int = 1_000_000,
    respect_gitignore: bool = True,
) -> List[Path]:
    root = root.resolve()
    include_ext = include_ext or DEFAULT_CODE_EXTENSIONS
    exclude = list(exclude or [])
    include = list(include or [])
    git_pats = _gitignore_patterns(root) if respect_gitignore else []
    special_names = {"Dockerfile", "Makefile", "CMakeLists.txt"}
    files: List[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in include_ext and path.name not in special_names:
            continue
        if _is_ignored(path, root, git_pats, exclude):
            continue
        if include:
            rel = path.relative_to(root).as_posix()
            if not any(tok in rel for tok in include):
                continue
        try:
            if path.stat().st_size > max_file_size:
                logger.info("Skipping large file (%s bytes): %s", path.stat().st_size, path)
                continue
        except OSError:
            continue
        files.append(path)
    return files


def build_tree_overview(root: Path, files: Sequence[Path]) -> str:
    root = root.resolve()
    lines = [f"{root.name}/"]
    rels = [f.relative_to(root).as_posix() for f in files]
    seen_dirs: Set[str] = set()
    for rel in sorted(rels):
        parts = rel.split("/")
        for i in range(len(parts) - 1):
            d = "/".join(parts[: i + 1])
            if d not in seen_dirs:
                seen_dirs.add(d)
                lines.append(f"{'  ' * i}{parts[i]}/")
        lines.append(f"{'  ' * (len(parts) - 1)}{parts[-1]}")
    return "\n".join(lines)


def file_to_markdown(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    lang = LANG_MAP.get(path.suffix.lower(), "")
    if path.name == "Dockerfile":
        lang = "dockerfile"
    if path.name == "Makefile":
        lang = "make"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        text = f"# Error reading file: {exc}\n"
    return f"### `{rel}`\n\n```{lang}\n{text.rstrip()}\n```\n"


def convert_code_project(
    root: Path,
    *,
    include_ext: Optional[Set[str]] = None,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    max_file_size: int = 1_000_000,
    single_file: bool = True,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Not a directory: {root}")

    files = collect_code_files(
        root,
        include_ext=include_ext,
        include=include,
        exclude=exclude,
        max_file_size=max_file_size,
    )
    if not files:
        logger.warning("No source files found under %s", root)
        return []

    logger.info("Code project: %d file(s) selected under %s", len(files), root)
    written: List[Path] = []

    if single_file:
        tree = build_tree_overview(root, files)
        parts = [
            f"# Code project: `{root.name}`\n",
            f"Root: `{root}`\n",
            f"Files: {len(files)}\n",
            "## Directory tree\n",
            f"```\n{tree}\n```\n",
            "## Source files\n",
        ]
        for f in files:
            parts.append(file_to_markdown(f, root))
        content = "\n".join(parts)
        if output_dir:
            output_dir = output_dir.expanduser().resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            out = output_dir / f"{root.name}_codebase.md"
        else:
            out = root / f"{root.name}_codebase.md"
        out.write_text(content, encoding="utf-8")
        written.append(out)
        logger.info("Wrote merged codebase Markdown: %s", out)
    else:
        for f in files:
            content = f"# `{f.relative_to(root).as_posix()}`\n\n" + file_to_markdown(f, root)
            if output_dir:
                output_dir = output_dir.expanduser().resolve()
                rel = f.relative_to(root).with_suffix(".md")
                out = output_dir / rel
                out.parent.mkdir(parents=True, exist_ok=True)
            else:
                out = f.with_suffix(".md")
            out.write_text(content, encoding="utf-8")
            written.append(out)
        logger.info("Wrote %d per-file Markdown outputs", len(written))

    return written
