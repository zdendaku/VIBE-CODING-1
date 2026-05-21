---
name: commit-message
description: "Conventional Commits formatter for this repository. MUST be used whenever Claude proposes or writes a git commit message — produces well-structured subject + body following the project's rules."
---

# Commit Message Conventions

Use this format **every single time** you author a git commit in this repo.

## Subject line

```
<type>(<scope>): <imperative summary>
```

* `<type>` — one of: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `build`, `ci`, `style`.
* `<scope>` — optional, lowercase, e.g. `mcp_server`, `cli`, `auth`.
* `<imperative summary>` — present tense ("add", not "added"), no period at the end.
* Maximum **72 characters**.

### Examples — good

* `feat(mcp_server): add python_complexity tool`
* `fix(cli): handle missing config file gracefully`
* `refactor(auth): extract token validation helper`

### Examples — bad

* `Updated stuff` (no type, vague)
* `feat: Added a new tool for analyzing python complexity.` (past tense + trailing period)
* `feat(mcp_server): added python_complexity tool to detect overly complex python source files with deep branching` (too long)

## Body (optional, but encouraged for non-trivial changes)

* Wrap at **72 characters** per line.
* Explain **what** and **why**, not **how** (the diff already shows how).
* Separate from subject with a blank line.

## Footer (optional)

* Use `BREAKING CHANGE:` prefix for breaking changes.
* Reference issues with `Refs #123` / `Closes #123`.

## Multi-change commits

Don't bundle unrelated changes. If you see two reasons in one diff, suggest
splitting before writing the message.

## Behaviour

* If the user asks for a commit message without giving a diff, ask for the
  diff or run `git diff --staged` (after confirming).
* Always print the proposed message in a fenced block so the user can copy it.
* Never auto-commit; the user runs `git commit`.
