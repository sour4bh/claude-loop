---
description: General continuous improvement
---

# Autonomous Loop: Generic

You are starting an autonomous work loop. This loop continues until max iterations, idle timeout, or user cancellation.

**Arguments provided:** $ARGUMENTS

## Parse Arguments

Extract from arguments:
- **prompt**: The work scope/task description (required)
- **--max-iterations N**: Maximum iterations (default: 50)
- **--resume**: Continue from existing state file
- **--tasks "..."**: Semicolon-separated tasks
- **--task-mode**: Process tasks sequentially (one per cycle)
- **--context "..."**: Tools and workflow context (persists across iterations)
- **--suggestions <preset>**: Override suggestion preset

## Your Task

### 1. Handle State File

**If `--resume` flag is present:**
- Read existing `.claude/loop-state.local.md`
- If file doesn't exist, report error: "No active loop to resume. Start without --resume."
- Continue from current state

**If NOT resuming (new loop):**
- If state file exists, warn user and overwrite
- Create new state file using the Write tool

Write to `.claude/loop-state.local.md`:
```markdown
---
mode: discovery
preset: generic
iteration: 1
max_iterations: [extracted or 50]
scope: [the prompt]
idle_streak: 0
exploration_streak: 0
task_started_at: 1
issues_found: 0
issues_fixed: 0
---

## Scope
[The work scope from the prompt]

## Context
[If --context provided, include it here. Otherwise omit this section.]
Available tools, workflow patterns, and other persistent context for each iteration.

## Current Focus
[What you're currently working on]

## Backlog
(Tasks discovered but not yet addressed)

## Completed
(What you've accomplished)

## Notes
(Observations, blockers, ideas)
```

### 2. Confirm Loop Started

Tell the user:
- What you'll be working on
- Preset: Generic
- Max iterations configured
- How to cancel: `/loop:cancel`

### 3. Work Autonomously

Execute the task from the prompt:
- When you complete something, look for the next thing to do
- Document findings and progress in the state file
- If the initial task is done, explore related improvements

### 4. Update State File Regularly

Keep the state file current:
- Update "Current Focus" when switching tasks
- Add completed items to "Completed" section
- Add discovered issues to "Backlog"
- Update notes with observations

### 5. Signal Cycle Completion (Optional)

When you complete a meaningful chunk of work:
```xml
<cycle_complete>
done: [what you accomplished]
found: [new issues discovered]
</cycle_complete>
```

## Work Philosophy

- **Stay focused** - Keep work aligned with the original scope
- **Document progress** - Update state file with your current focus
- **Be thorough** - Don't just do the minimum
- **Prioritize** - Important issues first, note minor ones for later

## The Loop Continues

The stop hook will prompt you to continue with contextual suggestions.
Only stops when:
- Max iterations reached
- 5 consecutive idle iterations (no progress)
- 3 consecutive exploration attempts with empty backlog (work exhausted)
- User runs `/loop:cancel`

**Your work persists in files between iterations.**
