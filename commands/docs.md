---
description: Documentation improvement
---

# Docs Loop

**Args:** $ARGUMENTS

## Arguments

- `prompt` (required): Work scope
- `--max-iterations N`: Limit (default: 50)
- `--resume`: Continue existing loop
- `--tasks "a; b; c"`: Seed backlog
- `--task-mode`: One task per cycle
- `--context "..."`: Persistent context


## Start Loop

**If `--resume`:** Read `.claude/loop-state.local.md`, error if missing.

**New loop:** Create state file:

```markdown
---
preset: docs
iteration: 1
max_iterations: [N or 50]
scope: [prompt]
idle_streak: 0
exploration_streak: 0
---

## Scope
[prompt]

## Context
[--context value if provided]

## Current Focus
[current task]

## Backlog
[discovered tasks]

## Completed
[done items]
```

Confirm: scope, preset (Docs), max iterations, cancel with `/loop:cancel`.

## Work

Execute the task. Document progress in state file. When done, explore related improvements.

**Docs:** Check README, verify examples work, document public APIs, update install instructions.

Update state file as you work. Signal completion with `<cycle_complete>done: X\nfound: Y</cycle_complete>`.

Loop continues until max iterations, 5 idle iterations, or `/loop:cancel`.
