# Project: Claude Code Setup Demo (Lesson 5)

Tento adresář ukazuje konfiguraci kódovacího agenta **Claude Code** s využitím:

- **MCP serverem** `project-insights` (vlastní, Python) a veřejným `fetch`
- **Skills** v `.claude/skills/` — neimperativně předávané znalosti
- **Subagents** v `.claude/agents/` — specializovaní pomocníci s vlastním tool-setem
- **Settings** v `.claude/settings.json` — permission allowlist, MCP serverů, env

## Žádné plugins, žádný marketplace

V souladu se zadáním jsou všechny rozšíření **lokální** (project-level konfigurace).
V `.claude/` ani `.mcp.json` se nepoužívá `plugins:` ani odkaz na marketplace.

## Jak to celé spolupracuje

1. Uživatel napíše prompt v Claude Code (např. *"udělej code review modulu X"*).
2. Claude přečte `CLAUDE.md` (tento soubor) → získá kontext projektu.
3. Najde relevantní **skill** (`python-style-guide`) → načte rubriku stylu.
4. Deleguje úkol na **subagent** `code-reviewer` přes nástroj `Agent`.
5. Subagent použije **MCP nástroje** `mcp__project-insights__python_complexity` apod.
6. Vrátí strukturovaný review report.

## Konvence

- Veškerý Python kód v projektu se píše podle skillu `python-style-guide`.
- Commit zprávy podle skillu `commit-message` (Conventional Commits).
- Recenze pomocí subagenta `code-reviewer`.
- Testy pomocí subagenta `test-writer`.
- Dokumentace pomocí subagenta `docs-writer`.

## Další dokumentace

- [`docs/contributing/CODE-STYLE-PYTHON.md`](docs/contributing/CODE-STYLE-PYTHON.md) —
  rozšířený Python style guide s příklady ze souborů projektu. Skill
  `python-style-guide` je závazná stručná rubrika pro agenta, tento
  dokument je výkladová verze pro lidi.
