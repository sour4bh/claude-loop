# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

claude-loop is a Claude Code plugin implementing Ralph Wiggum-style autonomous work loops. Based on Geoffrey Huntley's technique for iterative, self-referential AI development. The loop continues until max iterations, idle timeout, or user cancellation - there's no "done" state, just continuous discovery and improvement.

## Commands

```bash
# Build commands from presets (run after modifying presets)
python scripts/build.py

# Test suggestion rotation
python hooks/get-suggestion.py <preset> <iteration>
# Example: python hooks/get-suggestion.py ui 5
```

## Architecture

### Core Loop Mechanism

1. **Command files** (`commands/*.md`) - Claude Code skills that initialize state and start work
2. **Stop hook** (`hooks/stop-hook.sh`) - Intercepts after each response, increments iteration, injects continuation prompt
3. **State file** (`.claude/loop-state.local.md`) - Tracks progress, backlog, current focus across iterations

### Key Data Flow

```
User invokes /loop → Command creates state file → Claude works → Stop hook fires
                                                                      ↓
                     ← Hook injects continuation ← Checks termination conditions
```

### Two Modes

- **Exploitation**: Backlog has items → rotating suggestions keep focus on current work
- **Exploration**: Backlog empty → triggers Explore subagent to find more work

### Termination Conditions

- Max iterations reached (default 50)
- 5 consecutive idle iterations (no git changes AND no state file updates)
- 3 consecutive exploration attempts with empty backlog
- User runs `/loop:cancel`

## File Structure

- `src/template.md` - Base template for all command files
- `src/presets.toml` - Built-in preset definitions (ui, code-quality, docs, review, generic)
- `scripts/build.py` - Generates `commands/*.md` from template + presets
- `hooks/stop-hook.sh` - Main loop logic, state management, continuation injection
- `hooks/get-suggestion.py` - Returns rotating suggestion based on preset and iteration
- `hooks/hooks.json` - Registers stop hook with Claude Code

## Customization

User presets go in `~/.config/claude-loop/presets.toml`. After adding, run `/loop:build` or `python scripts/build.py` to generate new commands.

## Development

### Local Testing

```bash
# Test plugin without installing
claude --plugin-dir ./

# Debug hook execution
claude --debug
```

### Stop Hook Decision Control

The stop hook returns JSON to control continuation:
```json
{"decision": "block", "reason": "Continuation prompt shown to Claude"}
```

- `"decision": "block"` - Forces continuation with the reason as context
- Exit code 0 with JSON for structured control
- Hook reads from stdin (JSON with `transcript_path` field)

### Environment Variables in Hooks

- `CLAUDE_PLUGIN_ROOT` - Absolute path to plugin directory
- `CLAUDE_PROJECT_DIR` - Project root where Claude is running

### Cross-Platform Notes

- sed syntax differs: use `$(uname)` check for Darwin vs Linux
- Always quote shell variables: `"$VAR"` not `$VAR`
- Validate numeric values before arithmetic: `[[ "$VAR" =~ ^[0-9]+$ ]]`

## Requirements

- Python 3.11+ (for `tomllib`)
- `jq` (for JSON parsing in hook)
- Git (for idle detection via diff)
