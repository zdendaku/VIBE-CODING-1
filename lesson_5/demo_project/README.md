# demo_project

Maličký Python modul, na kterém je možné vyzkoušet:

- subagent `code-reviewer` (najde porušení style-guide + TODO)
- subagent `test-writer` (napíše pytest pokrytí pro `orders.py`)
- MCP nástroje `project-insights` (LOC, complexity, todos)

## Příklady promptů v Claude Code

```
> review the orders.py module
```

```
> write pytest tests for demo_project/orders.py
```

```
> give me a project summary of this repo
```
