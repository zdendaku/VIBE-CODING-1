# Lesson 5 — Nastavení kódovacího agenta (Claude Code)

**Autor:** zdendaku@gmail.com
**Kódovací agent:** Claude Code
**Použito:** MCP Servers, Skills, Subagents
**Nepoužito (záměrně, viz zadání):** Plugins, Marketplace

---

## Cíl

Ukázat funkční konfiguraci kódovacího agenta **Claude Code**, který:

- má dva **MCP servery** (jeden vlastní v Pythonu, jeden veřejný)
- má dva **Skills** — sdílené znalosti vkládané do kontextu na vyžádání
- má tři **Subagenty** — specializované pomocníky se samostatným tool-setem
- má restriktivní **permission allowlist** v `.claude/settings.json`

V repozitáři nejsou žádné `plugins:`, `marketplace`, ani odkazy na ně.

---

## Struktura projektu

```
lesson_5/
├── README.md                 ← tento přehled
├── CLAUDE.md                 ← projektový kontext, který Claude načte první
├── .mcp.json                 ← konfigurace MCP serverů (project-level)
├── .claude/
│   ├── settings.json         ← permission allowlist + enabled MCP servery
│   ├── skills/
│   │   ├── python-style-guide/SKILL.md
│   │   └── commit-message/SKILL.md
│   └── agents/
│       ├── code-reviewer.md
│       ├── test-writer.md
│       └── docs-writer.md
├── mcp_server/               ← vlastní stdio MCP server (Python)
│   ├── server.py
│   ├── pyproject.toml
│   └── README.md
└── demo_project/             ← cíl, na kterém lze setup vyzkoušet
    ├── orders.py
    └── README.md
```

---

## 1. MCP servery

Konfigurace v [`.mcp.json`](.mcp.json):

| Server             | Typ   | Účel                                                            |
|--------------------|-------|-----------------------------------------------------------------|
| `project-insights` | stdio | **Vlastní Python MCP server** – metriky a TODO scanner pro projekt |
| `fetch`            | stdio | Veřejný `mcp-server-fetch` – stahování HTTP obsahu              |

### Vlastní server `project-insights` (Python)

Implementovaný pomocí `mcp` Python SDK (`FastMCP`). Vystavuje 4 nástroje:

| Tool                     | Popis                                          |
|--------------------------|------------------------------------------------|
| `count_lines_of_code`    | LOC / blank / comments per file                |
| `find_todos`             | TODO / FIXME / XXX / HACK markery v Python souborech |
| `python_complexity`      | Skóre složitosti pro jeden soubor              |
| `project_summary`        | Souhrn projektu (LOC, top 5 souborů)           |

Zdroj v [`mcp_server/server.py`](mcp_server/server.py).

V Claude Code se nástroje objevují jako `mcp__project-insights__<tool>`.

---

## 2. Skills (`.claude/skills/`)

Skills jsou Markdown soubory s YAML frontmatterem. Claude je objeví
automaticky díky `setting_sources=["project"]` a invokuje podle `description`,
**bez** toho aby je uživatel jmenoval v promptu.

| Skill                | Kdy se aktivuje                                              |
|----------------------|--------------------------------------------------------------|
| `python-style-guide` | Pokaždé, když se píše / refaktoruje / reviewuje Python kód   |
| `commit-message`     | Pokaždé, když se má vygenerovat commit message               |

Jejich SKILL.md obsahují **kompletní rubriku** (naming, typing, imports, error
handling, Conventional Commits formát) — Claude je čte jako autoritativní
zdroj pravdy.

---

## 3. Subagents (`.claude/agents/`)

Filesystem-based subagenty: YAML frontmatter (name, description, tools, model)
+ Markdown body jako system prompt.

| Subagent        | Spouští se na                                  | Vlastní tools                                          |
|-----------------|------------------------------------------------|--------------------------------------------------------|
| `code-reviewer` | "udělej review", "audit", "second opinion"     | Read, Grep, Glob, Bash, mcp__project-insights__*       |
| `test-writer`   | "napiš testy", "coverage", "edge cases"        | Read, Write, Edit, Glob, Grep, Bash                    |
| `docs-writer`   | "napiš README", "doc", "document this"         | Read, Write, Edit, Glob, Grep                          |

Každý má vlastní omezený toolset (princip least-privilege) a vlastní model
(sonnet vs. haiku) podle náročnosti úlohy.

---

## 4. Settings (`.claude/settings.json`)

Bezpečnostní vrstva projektu:

- **Permission allowlist** — explicitně povolené nástroje a vzory cest.
- **Permission denylist** — zakázané destruktivní příkazy (`rm -rf`, `git push`, čtení `.env`).
- **enabledMcpjsonServers** — explicitně schválené MCP servery.
- **env** — projektové proměnné prostředí.

Žádný `plugins:` klíč v souboru.

---

## 5. Demo projekt

V [`demo_project/orders.py`](demo_project/orders.py) je úmyslně zanesených
pár drobností (chybí type hint u `apply_discount`, TODO marker), aby bylo
hned vidět, jak subagent `code-reviewer` a MCP nástroj `find_todos` reagují.

---

## Instalace

```bash
# 1. Klonuj repo / přepni se do adresáře
cd lesson_5

# 2. Nainstaluj vlastní MCP server
cd mcp_server
uv venv && source .venv/bin/activate
uv pip install -e .
cd ..

# 3. Spusť Claude Code v tomto adresáři
claude
```

Při prvním spuštění tě Claude Code požádá o schválení MCP serverů
(`project-insights`, `fetch`) — schval je. Permission allowlist v
`.claude/settings.json` pak omezí, co všechno smí Claude bez ptaní udělat.

---

## Demo workflow

V Claude Code stačí napsat (žádný subagent / skill se nejmenuje explicitně):

```text
> Udělej code review pro demo_project/orders.py.
```

Co se stane uvnitř:

1. Claude přečte `CLAUDE.md` → pozná konvence projektu.
2. Spustí subagent `code-reviewer` (matchnul popis).
3. Ten načte skill `python-style-guide` → má rubriku.
4. Zavolá `mcp__project-insights__python_complexity` na `orders.py`.
5. Zavolá `mcp__project-insights__find_todos` na demo_project/.
6. Vrátí strukturovaný report podle šablony v subagentově system promptu.

Další ukázkové prompty:

```text
> Napiš pytest testy pro demo_project/orders.py.
> Vygeneruj commit message pro mé staged změny.
> Dej mi project summary tohoto repa.
```

---

## Co tento setup ukazuje

- **Composability** — Skills + Subagenty + MCP nástroje se kombinují bez
  toho, abych je v promptu jmenoval. Auto-discovery dělá zbytek.
- **Least privilege** — každý subagent dostane jen ty nástroje, které
  opravdu potřebuje, a `settings.json` blokuje destruktivní operace.
- **Project-local** — vše je v `.claude/` a `.mcp.json` v repu, sdíleno
  s týmem přes git, žádné globální závislosti ani marketplace.
- **Reprodukovatelnost** — nový kolega `git clone` + `claude` a má
  totožný setup jako já.
