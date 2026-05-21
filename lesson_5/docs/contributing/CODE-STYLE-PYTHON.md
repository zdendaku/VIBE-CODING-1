# Python Code Style Guidelines — lesson_5

## Purpose

This document is the long-form Python style guide for the **lesson_5**
project (Claude Code setup demo with MCP server, Skills and Subagents).
It expands on the rules in [`.claude/skills/python-style-guide/SKILL.md`](../../.claude/skills/python-style-guide/SKILL.md)
— that skill is the binding rubric for the agent; this document is the
human-readable reference with worked examples taken from the actual
project files (`mcp_server/server.py`, `demo_project/orders.py`).

Whenever the two disagree, the SKILL.md wins.

## General Principles

### 1. Follow modern Python standards

- Target **Python 3.10+** — use the modern syntax (`list[int]`, `int | None`).
- Adhere to PEP 8 for layout and PEP 257 for docstrings.
- Embrace Pythonic idioms; "explicit is better than implicit".

### 2. Code Quality

- Write readable, self-documenting code — names carry the intent.
- Type-hint every public function (arguments + return).
- Prefer composition over inheritance.
- Follow DRY, but don't pre-abstract — three similar lines are fine.

## File and Project Structure

### File naming

Use `snake_case` for all file and directory names:

```text
✅ server.py
✅ orders.py
❌ Server.py
❌ orderProcessing.py
```

### Project layout

The lesson_5 repo is intentionally flat — there is no `src/` layout
because the project is a Claude Code setup demo, not a distributable
package.

```text
lesson_5/
├── .claude/
│   ├── agents/                    # filesystem-based subagents (.md)
│   ├── skills/                    # filesystem-based skills (SKILL.md)
│   └── settings.json
├── .mcp.json                      # project-level MCP server config
├── CLAUDE.md
├── README.md
├── docs/
│   └── contributing/
│       └── CODE-STYLE-PYTHON.md   # this document
├── mcp_server/
│   ├── server.py                  # FastMCP stdio server
│   ├── pyproject.toml
│   └── README.md
└── demo_project/
    ├── __init__.py
    ├── orders.py                  # target for code-reviewer / test-writer
    └── README.md
```

### Module organization

Every `.py` file starts with:

1. A short module docstring (one-line summary + optional details).
2. `from __future__ import annotations` (always — even for new code).
3. Standard library imports.
4. Third-party imports.
5. Local imports.

Groups are separated by **one blank line**, each group sorted alphabetically.

Real example from `mcp_server/server.py`:

```python
"""Project Insights MCP Server.

Custom MCP server providing project-analysis tools that are not part of
Claude Code's built-in toolset.
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
```

## Naming Conventions

### Variables and functions

`snake_case`, descriptive but not overly long.

```python
package_count = 0
is_initialized = False
config_path = Path("/etc/config.yaml")


def count_lines_of_code(directory: str = ".") -> str:
    """Count lines of code in every Python file under ``directory``."""
    ...


def _iter_python_files(root: Path) -> list[Path]:
    """Private helper — leading underscore."""
    ...
```

### Classes

`PascalCase` for class names.

```python
class FileStat:
    """Aggregated statistics for a single source file."""


class Order:
    """Represents a single customer order."""
```

### Constants

`UPPER_SNAKE_CASE`, declared at module top after imports.

```python
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b[:\s]*(.*)", re.IGNORECASE)
MAX_RETRIES = 3
```

### Private members

A single leading underscore marks "internal use". Don't use the
double-underscore name-mangling form unless you have a concrete reason.

```python
class OrderProcessor:
    def __init__(self) -> None:
        self._cache: dict[int, Order] = {}

    def _flush_cache(self) -> None:
        ...
```

### Type aliases

`PascalCase`.

```python
UserId = int
PackageRegistry = dict[str, "PackageInfo"]
```

## Type Hints

### Modern syntax (Python 3.10+)

Always prefer the built-in generic syntax. **Do not** import `List`,
`Dict`, `Optional` from `typing`.

```python
# Good
def total(order: Order) -> float: ...
def get_files(root: Path) -> list[Path]: ...
def find_user(uid: int) -> User | None: ...
def load_config(path: Path) -> dict[str, Any]: ...

# Bad
from typing import Dict, List, Optional
def total(order: Order) -> float: ...
def get_files(root: Path) -> List[Path]: ...                  # use list[Path]
def find_user(uid: int) -> Optional[User]: ...                # use User | None
def load_config(path: Path) -> Dict[str, Any]: ...            # use dict[str, Any]
```

`from __future__ import annotations` is required at the top of every
module so forward references and `X | Y` work uniformly.

### Dataclasses for structured data

Prefer `@dataclass` over hand-rolled `__init__` for plain data carriers.

```python
from dataclasses import dataclass


@dataclass
class FileStat:
    path: str
    lines: int
    code: int
    blank: int
    comments: int


@dataclass
class Order:
    """Represents a single customer order."""

    order_id: int
    customer: str
    items: list[tuple[str, float, int]]  # (name, unit_price, qty)
```

### Protocols for structural typing

Use `typing.Protocol` when you need a "shape" without committing to a
base class.

```python
from typing import Protocol


class HasName(Protocol):
    name: str


def greet(thing: HasName) -> str:
    return f"Hello, {thing.name}"
```

## Code Formatting

### Line length and indentation

- Maximum line length: **100 characters** (matches the SKILL).
- 4 spaces per indent level — never tabs.
- No trailing whitespace.
- One blank line between methods, two between top-level definitions.
- Use `ruff format` — output must already match it.

### String formatting

- Default to **double quotes**.
- Use **f-strings** for interpolation. Never `%` or `.format()`.

```python
# Good
ticker = "AAPL"
price = 199.95
message = f"Stock {ticker} costs {price:.2f} USD"

# Bad
message = "Stock %s costs %.2f USD" % (ticker, price)         # old style
message = "Stock {} costs {:.2f} USD".format(ticker, price)   # outdated
```

For multi-line literal strings use `textwrap.dedent`:

```python
import textwrap

help_text = textwrap.dedent(
    """
    Usage:
      tool <command> [options]
    """
).strip()
```

### Lists, dicts and tuples

```python
# Short collections on a single line
packages = ["python3", "git", "vim"]
config = {"timeout": 300, "retry_count": 3}

# Long collections — one item per line, trailing comma
ignored_dirs = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
}
```

## Class Design

### Class member order

1. Class docstring
2. Class variables / constants
3. `__init__`
4. Special methods (`__repr__`, `__str__`, `__eq__`, …)
5. Public methods
6. Private methods (`_name`)

```python
class OrderRegistry:
    """In-memory registry of orders.

    Used by the demo workflow to demonstrate the code-reviewer and
    test-writer subagents.
    """

    MAX_ORDERS = 10_000

    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}

    def __repr__(self) -> str:
        return f"OrderRegistry(size={len(self._orders)})"

    def add(self, order: Order) -> None:
        """Register an order; overwrites any existing entry with same id."""
        self._orders[order.order_id] = order

    def get(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def _evict_oldest(self) -> None:
        ...
```

### Properties

Use `@property` for computed read-only values; add a setter only when
the assignment has side effects worth modelling.

```python
class Order:
    @property
    def total(self) -> float:
        """Order total without tax or discount."""
        return sum(price * qty for _, price, qty in self.items)
```

## Error Handling

### Domain-specific exceptions

Create a small hierarchy rooted at one project-specific base.

```python
class Lesson5Error(Exception):
    """Base class for project-specific errors."""


class ConfigurationError(Lesson5Error):
    """Raised when configuration cannot be loaded or is invalid."""


class AnalysisError(Lesson5Error):
    """Raised when a project-insights tool cannot complete."""

    def __init__(self, tool: str, reason: str) -> None:
        super().__init__(f"{tool}: {reason}")
        self.tool = tool
        self.reason = reason
```

### Patterns

- Catch the **most specific** exception you can name. Never `except:`,
  rarely `except Exception:`.
- Re-raise with `raise NewError(...) from exc` so the chain is preserved.
- Don't use exceptions for control flow — return `None` or a sentinel.

```python
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON config file.

    Raises:
        ConfigurationError: file is missing, unreadable, or invalid JSON.
    """
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Config not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in {path}: {exc}") from exc
```

### Robust I/O in MCP tools

MCP tools must not raise to the host — they catch errors and return a
JSON document so the agent can act on the failure. Pattern from
`mcp_server/server.py`:

```python
@mcp.tool()
def count_lines_of_code(directory: str = ".") -> str:
    root = Path(directory).expanduser().resolve()
    if not root.exists():
        return json.dumps({"error": f"Directory not found: {root}"})
    ...
```

## Documentation

### Module docstrings

Short summary line, blank line, optional details. No Sphinx tags.

```python
"""Project Insights MCP Server.

Custom MCP server providing project-analysis tools that are not part of
Claude Code's built-in toolset:

  * count_lines_of_code  - count Python LOC per file in a directory
  * find_todos           - list TODO / FIXME / XXX markers across a tree
  * python_complexity    - rough complexity score
  * project_summary      - aggregate stats
"""
```

### Function and method docstrings

Use **Google-style** docstrings. Keep them short; the type hints already
carry the type info, so the prose can focus on behaviour.

```python
def python_complexity(file_path: str) -> str:
    """Compute a rough complexity score for a single Python file.

    The score counts function definitions, branches (``if``/``elif``/``else``),
    loops, ``try``/``except`` blocks, and ``return`` statements. Larger numbers
    suggest the file is harder to maintain.

    Args:
        file_path: Absolute or user-relative path to a ``.py`` file.

    Returns:
        JSON-encoded ``{counters, score, verdict}`` document. ``verdict`` is
        one of ``"low"``, ``"medium"``, ``"high"``.

    Raises:
        Never — errors are returned as ``{"error": ...}`` instead.
    """
    ...
```

Skip docstrings only for trivially obvious one-liners (e.g. `__repr__`).

## Testing

### Test layout

- Tests live in `tests/`, mirroring the package layout.
- Use **`pytest`**, never `unittest`.
- File name: `test_<module>.py`.
- Function name: `test_<behavior>_<expected>`.
- One behaviour per test.

```python
# tests/test_orders.py
from __future__ import annotations

import pytest

from demo_project.orders import Order, apply_discount, format_receipt, total


@pytest.fixture
def sample_order() -> Order:
    return Order(
        order_id=1,
        customer="Alice",
        items=[("Coffee", 3.50, 2), ("Croissant", 2.00, 1)],
    )


def test_total_sums_all_items(sample_order: Order) -> None:
    assert total(sample_order) == pytest.approx(9.00)


def test_format_receipt_includes_customer_name(sample_order: Order) -> None:
    receipt = format_receipt(sample_order)
    assert "Alice" in receipt
    assert "TOTAL: 9.00" in receipt


@pytest.mark.parametrize(
    "amount, percent, expected",
    [
        (100, 10, 90),
        (100, 0, 100),
        (50, 50, 25),
    ],
    ids=["10pct", "zero", "half"],
)
def test_apply_discount_simple_cases(amount: float, percent: float, expected: float) -> None:
    assert apply_discount(amount, percent) == pytest.approx(expected)
```

### Fixtures and helpers

- Prefer **`tmp_path`** and **`monkeypatch`** fixtures over mocking
  everything; tests should exercise real code paths.
- Put cross-file fixtures in `tests/conftest.py`.
- Don't mock filesystem operations if `tmp_path` works.

```python
# tests/conftest.py
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_python_tree(tmp_path: Path) -> Path:
    """Build a tiny Python project tree for MCP-tool integration tests."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "core.py").write_text(
        "def f() -> int:\n    return 1  # TODO: docstring\n"
    )
    return tmp_path
```

## Logging

In any code that is not strictly a script entry point, use the standard
`logging` module — never `print`. The library is the producer of log
records; the host decides where they go.

```python
import logging

logger = logging.getLogger(__name__)


def install_package(name: str) -> bool:
    logger.info("Installing package: %s", name)
    try:
        ...
    except OSError as exc:
        logger.exception("Installation failed: %s", name)
        raise
    return True
```

For the MCP server in this project we keep logging minimal — `FastMCP`
sends stdio to Claude Code, so anything written to `stdout` would
corrupt the protocol. Use `logger` (which goes to stderr by default)
or skip logging entirely.

## Async Programming

The project has no asynchronous code today — the MCP server runs on
`mcp.run()` synchronously over stdio. If you add async, follow these
rules:

- Never call `time.sleep` inside `async def`; use `await asyncio.sleep`.
- Bound concurrency with a `asyncio.Semaphore`.
- Always wrap user-facing async entry points with `try`/`except` so a
  single failing task does not crash the whole gather.

```python
import asyncio


async def fan_out(items: list[str], worker: callable, limit: int = 5) -> dict[str, bool]:
    sem = asyncio.Semaphore(limit)

    async def run_one(item: str) -> tuple[str, bool]:
        async with sem:
            return item, await worker(item)

    pairs = await asyncio.gather(*(run_one(i) for i in items))
    return dict(pairs)
```

## MCP Server Patterns

The MCP server in this project uses **FastMCP** — the high-level helper
from the `mcp` Python SDK. Conventions:

### Tool definition

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-insights")


@mcp.tool()
def project_summary(directory: str = ".") -> str:
    """High-level summary of a project.

    Returns a JSON-encoded ``{python_files, total_code_lines, top_files}``
    document. Always returns a string; errors are encoded as
    ``{"error": "..."}``.
    """
    ...
```

### Tool design rules

- **Inputs:** primitive types only (`str`, `int`, `float`, `bool`). Avoid
  rich Python types in signatures — they don't round-trip through JSON.
- **Outputs:** always a JSON string. Never raise to the host.
- **Defaults:** every parameter that has a sensible default should have
  one, so the agent can call the tool with just a hint.
- **Determinism:** the same arguments should produce the same result;
  no hidden state across calls.
- **Side effects:** avoid them. Read-only tools are easy for the agent
  to use; write tools require permission gating in `.claude/settings.json`.

### Entry point

```python
def main() -> None:
    try:
        mcp.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
```

## Project Tooling

### `pyproject.toml` (minimal MCP-server pattern)

The full file lives at `mcp_server/pyproject.toml`. Key shape:

```toml
[project]
name = "project-insights-mcp"
version = "0.1.0"
description = "Custom MCP server with project-analysis tools for Claude Code."
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.2.0",
]

[project.scripts]
project-insights-mcp = "server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["."]
```

### Optional formatters & linters

The project doesn't enforce a specific toolchain in CI today, but if you
run anything locally, use:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]
ignore = []

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = "-ra -q"
```

`ruff` covers both formatting (`ruff format`) and linting + import
sorting, which is why the project skips `black`/`isort`/`flake8` as
separate tools.

### Pre-commit (optional)

Not configured by default; if you want hooks locally, the minimal
config that matches this style guide is:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Forbidden patterns

Never:

- mutable default arguments (`def f(items=[])`)
- bare `except:` or `except Exception:` at the top level
- `eval`, `exec`, or `pickle` on untrusted input
- `time.sleep` inside `async def`
- `print()` in library / MCP-server code
- wildcard imports (`from x import *`)
- relative imports across packages (`from ..foo import bar`)
- naming `l`, `I`, `O` as variables

## Relationship to the SKILL

The Claude Code agent reads
`.claude/skills/python-style-guide/SKILL.md` (loaded automatically when
this project is opened). That skill is the **terse rubric** the agent
follows mechanically. This document expands the same rules with
context, real-project examples, and rationale — it is meant for
humans reading the repo, not for the agent.

If you change a rule, update **both** files.

---

*Created: 2026-05-21*
*Last updated: 2026-05-21*
