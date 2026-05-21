# VIBE-CODING-1 — Homework (zdendaku)

Odevzdané úkoly z kurzu **Global Classes — Vibe Coding 1**.

Originální studijní podklady kurzu:
<https://github.com/Global-Classes-CZE/Vibe-Coding-1>

## Obsah

| Lekce | Téma | Adresář |
|-------|------|---------|
| 1 | Python skript volající LLM API s tool use | [`lesson_1/`](lesson_1/) |
| 5 | Nastavení kódovacího agenta (Claude Code) — MCP, Skills, Subagents | [`lesson_5/`](lesson_5/) |

## Aktualizace obsahu (sync)

Tento repozitář je publish kopií pracovního adresáře v parent course repu.
Pro synchronizaci slouží [`sync.sh`](sync.sh):

```bash
./sync.sh                      # rsync z parent repa, vypíše git status
./sync.sh --dry-run            # ukáže, co by se změnilo, nic nezapisuje
./sync.sh --commit "msg"       # sync + commit
./sync.sh --push "msg"         # sync + commit + push
```

Source path je zadrátovaný v sync.sh (`SRC=...`); upravit podle vlastního
umístění.

## Autor

zdendaku@gmail.com
