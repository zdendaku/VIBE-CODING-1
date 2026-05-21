# project-insights — vlastní MCP server

Stdio MCP server poskytující nástroje pro rychlou analýzu projektu:

| Nástroj | Popis |
|---------|-------|
| `count_lines_of_code` | Spočítá řádky kódu / prázdné / komentáře po souborech |
| `find_todos` | Najde značky TODO / FIXME / XXX / HACK v Python souborech |
| `python_complexity` | Hrubá metrika složitosti (větve, smyčky, funkce) pro jeden soubor |
| `project_summary` | Souhrn: počet souborů, celkové LOC, top 5 největších souborů |

## Instalace

```bash
cd mcp_server
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Lokální spuštění

```bash
python server.py
```

## Připojení do Claude Code

Server je v `.mcp.json` projektu zaregistrovaný pod jménem `project-insights`,
takže Claude Code ho spustí automaticky. Jeho nástroje se v promptu objeví
jako `mcp__project-insights__count_lines_of_code` atd.
