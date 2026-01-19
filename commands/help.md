---
description: Interactive wizard to formulate and invoke a loop
---

# Loop Help

Generate a custom `/loop` command based on context.

## Steps

1. **Gather context:** git changes, project structure, TODOs
2. **Ask:** goal (audit/fix/improve/document), focus areas, exploratory vs task-based
3. **Identify tools:** MCP servers (`mcp__*`), slash commands, automation
4. **Generate command** with specific prompt, tools/workflow embedded, tasks, max-iterations

## Output Format

```
/loop:preset "Scope description.

TOOLS: mcp__x, /deploy
WORKFLOW: find → fix → test → continue" \
  --tasks "task1; task2" \
  --max-iterations 25
```

## Parameters

| Param | Description |
|-------|-------------|
| `prompt` | Work scope (required) |
| `--max-iterations N` | Limit (default: 50) |
| `--tasks "..."` | Semicolon-separated |
| `--task-mode` | One task per cycle |
| `--context "..."` | Persistent context |
| `--suggestions <preset>` | Override suggestions |
| `--resume` | Continue existing |

## Presets

`generic`, `ui`, `code-quality`, `docs`, `review`
