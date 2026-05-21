---
name: python-style-guide
description: "Project Python style guide. MUST be applied whenever Claude writes, reviews, or refactors Python code in this repository — covers naming, typing, imports, error handling, and docstrings."
---

# Python Style Guide

This skill is the single source of truth for Python style in this project.
Apply every rule below whenever you generate or modify `.py` files.

## 1. Formatting

- Use **4 spaces** for indentation, never tabs.
- Maximum line length **100 characters**.
- One blank line between methods, two between top-level definitions.
- Run `ruff format` mentally — output must already match it.

## 2. Naming

| Kind            | Convention                | Example          |
|-----------------|---------------------------|------------------|
| Module          | `snake_case`              | `data_loader.py` |
| Class           | `PascalCase`              | `OrderProcessor` |
| Function / var  | `snake_case`              | `parse_invoice`  |
| Constant        | `UPPER_SNAKE_CASE`        | `MAX_RETRIES`    |
| Private member  | leading underscore        | `_internal_id`   |
| Type alias      | `PascalCase`              | `UserId`         |

## 3. Imports

- Order: **stdlib → third-party → local**, separated by blank lines.
- Always **absolute** imports inside the package (no relative `..foo`).
- Never use wildcard `from x import *`.
- Sort each group alphabetically.

## 4. Type hints

- **All public functions** must be fully annotated (arguments + return).
- Use `from __future__ import annotations` at the top of every file.
- Prefer `list[int]` over `List[int]` (Python 3.10+).
- For optional values use `int | None`, not `Optional[int]`.

## 5. Docstrings

- Every module, public class, and public function has a docstring.
- Style: short summary line, blank line, optional details — no Sphinx tags.
- Skip docstrings for trivially obvious one-liners (e.g. `__repr__`).

## 6. Error handling

- Never `except:` bare or `except Exception:` at the top level.
- Catch the most specific exception you can name.
- Re-raise with `raise NewError(...) from exc` to preserve the chain.
- Don't use exceptions for control flow.

## 7. Strings & f-strings

- Use **double quotes** by default; single quotes only inside doubles.
- Use **f-strings** for interpolation — never `%` or `.format()`.
- For multi-line strings prefer `textwrap.dedent`.

## 8. Forbidden patterns

- No mutable default arguments (`def f(x=[])`).
- No `print()` in library code — use `logging`.
- No `eval`, no `exec`, no `pickle` on untrusted input.
- No `time.sleep` in async code — use `await asyncio.sleep`.

## 9. Tests

- Tests live in `tests/`, mirror the package layout.
- Use `pytest`, not `unittest`.
- Name tests `test_<behavior>_<expected>`.
- Each test asserts **one** behavior.

## 10. Output rules

When you finish editing:

1. Mention which rules were applied (one line each).
2. If a rule conflicts with existing code, prefer the rule and adjust the
   surrounding lines.
3. If you cannot follow a rule, explain why explicitly — never silently skip.
