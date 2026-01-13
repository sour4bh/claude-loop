---
description: Interactive wizard to formulate and invoke a loop
---

# Loop Help - Command Generator

Help the user craft the perfect `/loop` command for their situation.

## Your Task

You'll analyze the current context and generate a custom `/loop` command.

### 1. Gather Context

Look at:
- Recent git changes (`git log --oneline -10`, `git diff --stat`)
- Project structure (key directories, tech stack)
- Any TODO comments or FIXME markers
- Open files or recent work patterns

### 2. Ask Clarifying Questions

Use the AskUserQuestion tool to understand:
- What's the main goal? (audit, fix, improve, document)
- Any specific areas of focus?
- Should work be exploratory (discovery) or task-based?

### 3. Identify Available Tools & Workflow

Before generating the command, identify:
- **MCP servers** available (check conversation context for `mcp__*` tools)
- **Slash commands** that could help (deployment, testing, etc.)
- **Automation tools** (browser control, API testing, etc.)
- **Preferred workflow** (audit→fix→test→deploy, or similar)

This context should be embedded in the prompt so the loop knows what tools to use.

### 4. Generate Custom Command

Based on context, craft a `/loop` command with:
- **Specific, actionable prompt** - not generic
- **Tools & workflow embedded** - so each iteration knows what's available
- **Relevant `--tasks`** if they mentioned specific items
- **Appropriate `--max-iterations`** based on scope
- **Preset suggestion** if one fits well

**Important:** The prompt is the only context that persists across iterations. Include:
1. The goal/scope
2. Available tools (MCP servers, slash commands, automation)
3. Workflow pattern (e.g., "find→fix→test→continue")

### 5. Present and Confirm

Show the user the command with embedded context:
```
Based on your project and goals, I suggest:

/loop "Improve auth flow error handling.

TOOLS: mcp__db__* for queries, /deploy for releases
WORKFLOW: find issue → fix → test → continue" \
  --tasks "handle token expiry; add retry logic; improve error messages" \
  --max-iterations 25

This will systematically work through auth improvements. Start?
```

### 6. Execute on Confirmation

When user confirms:
- Run the command as if they typed it
- Use the Skill tool to invoke `/loop` with the generated arguments

## Available Parameters

| Parameter | Description |
|-----------|-------------|
| `prompt` | Work scope (required) |
| `--max-iterations N` | Safety limit (default: 50) |
| `--tasks "..."` | Semicolon-separated tasks |
| `--task-mode` | Process tasks sequentially |
| `--context "..."` | Tools & workflow (persists across iterations) |
| `--suggestions <preset>` | Override suggestion preset |
| `--resume` | Continue from existing state |

## Available Presets

- `generic` - General continuous improvement
- `ui` - UI audit and visual consistency
- `code-quality` - Code quality and technical debt
- `docs` - Documentation improvement
- `review` - Code review and quality check

## Example Outputs

**UI audit with browser automation:**
```
/loop:ui "Audit all forms in the dashboard.

TOOLS: mcp__browser__* for automation, mcp__db__* for data checks
WORKFLOW: navigate → test → screenshot issues → fix → verify → continue" \
  --tasks "check validation; test error states; verify accessibility" \
  --max-iterations 30
```

**Code quality with deployment:**
```
/loop:code-quality "Reduce type assertions and improve error handling.

TOOLS: /deploy for preview deploys, /logs for error checking
WORKFLOW: find issue → fix → deploy preview → verify → continue" \
  --max-iterations 40
```

**Database-heavy work:**
```
/loop "Optimize slow queries and add missing indexes.

TOOLS: mcp__supabase__execute_sql, mcp__supabase__get_advisors
WORKFLOW: get advisors → analyze → fix → test query → continue" \
  --tasks "check N+1 queries; add missing indexes; optimize joins"
```

**Simple exploration (no special tools):**
```
/loop "General improvements to the auth module" \
  --suggestions code-quality
```
