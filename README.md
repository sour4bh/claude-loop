# claude-loop

Ralph Wiggum-style autonomous work loop plugin for [Claude Code](https://claude.com/claude-code). Agentic coding with continuous improvement - no completion promises required.

> An evolution of the [Ralph Wiggum technique](https://ghuntley.com/ralph/) for iterative, self-referential AI development loops.

## Philosophy

Traditional autonomous loops (like the original Ralph loop) stop when a task is "complete." But software is never complete - there's always more to improve, fix, or explore. claude-loop embraces this:

- **No completion promise** - the loop doesn't wait for you to say "done"
- **Continuous discovery** - when one task finishes, find the next
- **Progress tracking** - state file tracks what's been found and fixed
- **Exploration/Exploitation balance** - rotating suggestions keep work productive

## Installation

### Option 1: Plugin install (recommended)

Add the marketplace and install:

```bash
/plugin marketplace add sour4bh/claude-loop
/plugin install loop@sour4bh
```


### Option 2: Clone to plugins directory

```bash
git clone https://github.com/sour4bh/claude-loop.git ~/.claude/plugins/claude-loop
```

### Option 3: Use with --plugin-dir flag

```bash
git clone https://github.com/sour4bh/claude-loop.git ~/claude-loop
claude --plugin-dir ~/claude-loop
```

### Verify installation

After installation, the following commands should be available in Claude Code:

```
/loop           - General autonomous loop
/loop:ui        - UI audit preset
/loop:code-quality - Code quality preset
/loop:docs      - Documentation preset
/loop:review    - Code review preset
/loop:cancel    - Stop the loop
/loop:build     - Rebuild after custom presets
/loop:help      - AI wizard for custom commands
```

## Usage

### Basic Usage

```bash
# Start a generic loop
/loop "refactor the authentication module"

# UI audit - finds and fixes issues continuously
/loop:ui "audit dashboard - find bugs, inconsistencies, UX issues"

# Code quality with max iterations
/loop:code-quality "fix type issues" --max-iterations 25

# Documentation improvement
/loop:docs "improve API documentation"
```

### With Tasks

```bash
# Provide specific tasks to seed the backlog
/loop:code-quality "improve auth module" --tasks "fix type errors; remove dead code; add logging"

# Task mode - process tasks sequentially (one per cycle)
/loop "refactor auth" --task-mode --tasks "extract tokens; add refresh; improve errors"
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | (required) | Work scope/task description |
| `--max-iterations N` | 50 | Safety limit for iterations |
| `--resume` | false | Continue from existing state file |
| `--tasks "..."` | - | Semicolon-separated tasks to seed backlog |
| `--task-mode` | false | Process tasks one per cycle |
| `--context "..."` | - | Tools/workflow context (persists across iterations) |
| `--suggestions <preset>` | - | Override suggestion preset (generic loop only) |

## How It Works

### The Loop Mechanism (Self-Referential Feedback Loop)

Like the classic Ralph Wiggum technique, claude-loop uses a **stop hook** to create an autonomous, self-correcting feedback loop:

1. **Start**: You invoke `/loop` with a task description
2. **State file**: Creates `.claude/loop-state.local.md` to track progress
3. **Work**: Claude works on the task autonomously (agentic coding)
4. **Stop hook intercepts**: After each response, the hook:
   - Increments iteration counter
   - Checks for idle state (no progress via git diff)
   - Injects continuation prompt with rotating suggestions
   - Reminds of original scope to prevent drift
5. **Self-correction**: Claude sees its previous work (git history, modified files) and continues iterating
6. **Continue**: Loop continues until max iterations, idle timeout, or `/loop:cancel`

This creates persistent iteration where each cycle builds on the last - the core of the Ralph technique.

### State File

The loop maintains state in `.claude/loop-state.local.md`:

```yaml
---
mode: discovery
preset: ui
iteration: 5
max_iterations: 50
scope: UI audit
idle_streak: 0
issues_found: 12
issues_fixed: 8
---

## Scope
UI audit of the dashboard

## Current Focus
Checking form validation

## Backlog
- Mobile responsive issues on /settings
- Console warning on /dashboard

## Completed
- Fixed button loading states
- Added error boundaries
```

### Continuation Modes

The loop switches between two modes based on state:

**Exploitation mode** (backlog has items):
- Rotating suggestions to keep focused on current work
- "Complete your current task before moving on"
- "Check your backlog and pick the highest priority item"

**Exploration mode** (backlog empty or cycle complete):
- Triggers the Explore subagent to search for more work
- Passes scope and state file as context
- Findings added to backlog automatically

### Termination Conditions

The loop stops when:
- **Max iterations reached** (default: 50)
- **Idle timeout** - 5 consecutive iterations with no git changes and no state file updates
- **Exploration exhaustion** - 3 consecutive exploration attempts with empty backlog
- **Manual cancel** - User runs `/loop:cancel`

### Cycle Signals (Optional)

Signal cycle completion explicitly in your work:

```xml
<cycle_complete>
done: Fixed 3 validation bugs
found: 2 new issues
</cycle_complete>
```

## Safeguards

- **Scope reminder** every iteration prevents divergence
- **Multi-signal idle detection** - requires both no git changes AND no state updates
- **State backup** before modifications
- **History archive** - completed loops saved to `.claude/loop-history/`

## Custom Presets

Create your own presets at `~/.config/claude-loop/presets.toml`:

```toml
[security]
description = "Security audit"
suggestions = [
    "Check for SQL injection vulnerabilities",
    "Look for XSS attack vectors",
    "Verify authentication flows",
    "Review input validation",
    "Check for sensitive data exposure",
]

[performance]
description = "Performance optimization"
suggestions = [
    "Profile the slowest endpoints",
    "Look for N+1 query patterns",
    "Check for unnecessary re-renders",
    "Review caching opportunities",
]
```

Then run `/loop:build` to generate `/loop:security` and `/loop:performance`.

## Requirements

- Claude Code 1.0.20+
- Python 3.11+ (for tomllib)
- `jq` (for JSON parsing in hook)

## File Structure

```
claude-loop/
├── .claude-plugin/
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Marketplace catalog
├── commands/
│   ├── loop.md              # Generic loop (generated)
│   ├── ui.md                # UI preset (generated)
│   ├── code-quality.md      # Code quality preset (generated)
│   ├── docs.md              # Docs preset (generated)
│   ├── review.md            # Review preset (generated)
│   ├── cancel.md            # Cancel command
│   ├── build.md             # Build command
│   └── help.md              # Help wizard
├── hooks/
│   ├── hooks.json           # Hook registration
│   ├── stop-hook.sh         # Main loop logic
│   ├── get-suggestion.py    # Rotating suggestions
│   └── analyze.py           # (unused) Haiku integration
├── scripts/
│   ├── build.py             # Command generator
│   ├── get-suggestion.py    # Suggestion fetcher
│   ├── analyze.py           # (unused) Haiku integration
│   └── stop-hook.sh         # Backup stop hook
├── src/
│   ├── template.md          # Command template
│   └── presets.toml         # Built-in presets
├── LICENSE
└── README.md
```

## References

### Attribution

This plugin builds on the **Ralph Wiggum technique**, an autonomous AI development methodology created by [Geoffrey Huntley](https://ghuntley.com). The technique enables iterative, self-referential development loops where an AI agent continuously improves code by reading its own previous work.

- **Geoffrey Huntley** ([@ghuntley](https://github.com/ghuntley)) - Creator of the Ralph Wiggum technique
  - [Original blog post](https://ghuntley.com/ralph/) - "Ralph is a Bash loop"
  - [how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum) - Methodology guide
- **Boris Cherny** ([@bcherny](https://github.com/bcherny)) - Official Anthropic implementation
  - [ralph-wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)

### Related Projects

| Project | Author | Description |
|---------|--------|-------------|
| [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) | Anthropic | Official plugin in claude-code repo |
| [ralph-loop](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop) | Anthropic | Official marketplace plugin |
| [ralph-claude-code](https://github.com/frankbria/ralph-claude-code) | @frankbria | Intelligent exit detection variant |
| [ralph-orchestrator](https://github.com/mikeyobrien/ralph-orchestrator) | @mikeyobrien | Multi-agent hat-based orchestration |
| [ralph-tui](https://github.com/subsy/ralph-tui) | @subsy | Terminal UI for Ralph loops |

### Further Reading

- [A Brief History of Ralph](https://www.humanlayer.dev/blog/brief-history-of-ralph) - HumanLayer
- [Ralph Wiggum: Autonomous Loops for Claude Code](https://paddo.dev/blog/ralph-wiggum-autonomous-loops/) - Paddo.dev
- [Inventing the Ralph Wiggum Loop](https://devinterrupted.substack.com/p/inventing-the-ralph-wiggum-loop-creator) - Dev Interrupted

## License

MIT - see [LICENSE](LICENSE)

## Contributing

Issues and PRs welcome at https://github.com/sour4bh/claude-loop
