#!/usr/bin/env python3
"""Project Insights MCP Server.

Custom MCP server providing project-analysis tools that are not part of
Claude Code's built-in toolset:

  * count_lines_of_code  - count Python LOC per file in a directory
  * find_todos           - list TODO / FIXME / XXX markers across a tree
  * python_complexity    - rough complexity score (functions / branches / loops)
  * project_summary      - aggregate stats (file count, total LOC, top files)

The server speaks the Model Context Protocol over stdio and is started by
Claude Code automatically based on the project's `.mcp.json` configuration.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-insights")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache"}
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b[:\s]*(.*)", re.IGNORECASE)


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


@dataclass
class FileStat:
    path: str
    lines: int
    code: int
    blank: int
    comments: int


def _stat_file(path: Path) -> FileStat:
    code = blank = comments = 0
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return FileStat(str(path), 0, 0, 0, 0)
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith("#"):
            comments += 1
        else:
            code += 1
    return FileStat(
        path=str(path),
        lines=code + blank + comments,
        code=code,
        blank=blank,
        comments=comments,
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def count_lines_of_code(directory: str = ".") -> str:
    """Count lines of code in every Python file under ``directory``.

    Returns a JSON document with per-file and aggregate counts.
    """
    root = Path(directory).expanduser().resolve()
    if not root.exists():
        return json.dumps({"error": f"Directory not found: {root}"})

    stats = [_stat_file(p) for p in _iter_python_files(root)]
    totals = {
        "files": len(stats),
        "code": sum(s.code for s in stats),
        "blank": sum(s.blank for s in stats),
        "comments": sum(s.comments for s in stats),
    }
    return json.dumps(
        {
            "root": str(root),
            "totals": totals,
            "files": [s.__dict__ for s in stats],
        },
        indent=2,
    )


@mcp.tool()
def find_todos(directory: str = ".") -> str:
    """Find TODO / FIXME / XXX / HACK markers in source files.

    Walks ``directory`` recursively (Python files only) and returns a JSON
    list of ``{file, line, tag, message}`` entries.
    """
    root = Path(directory).expanduser().resolve()
    if not root.exists():
        return json.dumps({"error": f"Directory not found: {root}"})

    hits: list[dict[str, Any]] = []
    for path in _iter_python_files(root):
        try:
            for lineno, line in enumerate(
                path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                match = TODO_RE.search(line)
                if match:
                    hits.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": lineno,
                            "tag": match.group(1).upper(),
                            "message": match.group(2).strip(),
                        }
                    )
        except OSError:
            continue
    return json.dumps({"root": str(root), "count": len(hits), "hits": hits}, indent=2)


@mcp.tool()
def python_complexity(file_path: str) -> str:
    """Compute a rough complexity score for a single Python file.

    The score counts function definitions, branches (``if``/``elif``/``else``),
    loops, ``try``/``except`` blocks, and ``return`` statements. Larger numbers
    suggest the file is harder to maintain and may deserve refactoring.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return json.dumps({"error": f"File not found: {path}"})
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as exc:
        return json.dumps({"error": f"SyntaxError: {exc}"})

    counters = {
        "functions": 0,
        "classes": 0,
        "branches": 0,
        "loops": 0,
        "tries": 0,
        "returns": 0,
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            counters["functions"] += 1
        elif isinstance(node, ast.ClassDef):
            counters["classes"] += 1
        elif isinstance(node, ast.If):
            counters["branches"] += 1
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            counters["loops"] += 1
        elif isinstance(node, ast.Try):
            counters["tries"] += 1
        elif isinstance(node, ast.Return):
            counters["returns"] += 1

    score = (
        counters["branches"] * 2
        + counters["loops"] * 2
        + counters["tries"] * 3
        + counters["functions"]
    )
    verdict = "low" if score < 15 else "medium" if score < 40 else "high"
    return json.dumps(
        {
            "file": str(path),
            "counters": counters,
            "score": score,
            "verdict": verdict,
        },
        indent=2,
    )


@mcp.tool()
def project_summary(directory: str = ".") -> str:
    """High-level summary of a project: file count, total LOC, top-5 largest files."""
    root = Path(directory).expanduser().resolve()
    if not root.exists():
        return json.dumps({"error": f"Directory not found: {root}"})

    stats = sorted(
        (_stat_file(p) for p in _iter_python_files(root)),
        key=lambda s: s.code,
        reverse=True,
    )
    return json.dumps(
        {
            "root": str(root),
            "python_files": len(stats),
            "total_code_lines": sum(s.code for s in stats),
            "top_files": [
                {"path": s.path, "code_lines": s.code} for s in stats[:5]
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start the MCP server on stdio."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
