#!/bin/bash
set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/.claude/loop-state.local.md"
BACKUP_FILE="$PROJECT_DIR/.claude/loop-state.backup.md"
HISTORY_DIR="$PROJECT_DIR/.claude/loop-history"
SCRIPTS_DIR="$(dirname "$0")"

# No state file = not in a loop
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Backup state file before any modifications
cp "$STATE_FILE" "$BACKUP_FILE" 2>/dev/null || true

# Parse state file with defensive defaults
parse_state() {
  local key="$1"
  local default="$2"
  local value
  value=$(sed -n "s/^${key}: *//p" "$STATE_FILE" | head -1)
  echo "${value:-$default}"
}

ITERATION=$(parse_state "iteration" "1")
MAX_ITER=$(parse_state "max_iterations" "50")
SCOPE=$(parse_state "scope" "unknown")
PRESET=$(parse_state "preset" "generic")
MODE=$(parse_state "mode" "discovery")
ISSUES_FOUND=$(parse_state "issues_found" "0")
ISSUES_FIXED=$(parse_state "issues_fixed" "0")
IDLE_STREAK=$(parse_state "idle_streak" "0")
EXPLORATION_STREAK=$(parse_state "exploration_streak" "0")

# Parse Context section (multi-line)
parse_section() {
  local section="$1"
  sed -n "/^## ${section}$/,/^## /p" "$STATE_FILE" | sed '1d;$d' | head -10
}
CONTEXT=$(parse_section "Context" 2>/dev/null || echo "")

# Validate numeric values
[[ "$ITERATION" =~ ^[0-9]+$ ]] || ITERATION=1
[[ "$MAX_ITER" =~ ^[0-9]+$ ]] || MAX_ITER=50
[[ "$ISSUES_FOUND" =~ ^[0-9]+$ ]] || ISSUES_FOUND=0
[[ "$ISSUES_FIXED" =~ ^[0-9]+$ ]] || ISSUES_FIXED=0
[[ "$IDLE_STREAK" =~ ^[0-9]+$ ]] || IDLE_STREAK=0
[[ "$EXPLORATION_STREAK" =~ ^[0-9]+$ ]] || EXPLORATION_STREAK=0

# Archive state file on completion
archive_state() {
  mkdir -p "$HISTORY_DIR"
  local timestamp
  timestamp=$(date +"%Y%m%d-%H%M%S")
  cp "$STATE_FILE" "$HISTORY_DIR/${timestamp}.md"
  rm -f "$STATE_FILE"
}

# Max iterations reached - archive and stop
if [[ $ITERATION -ge $MAX_ITER ]]; then
  archive_state
  exit 0
fi

# Idle detection - stop after 5 consecutive idle iterations
if [[ $IDLE_STREAK -ge 5 ]]; then
  archive_state
  jq -n --arg reason "🛑 Loop stopped after 5 idle iterations with no progress.
Scope was: $SCOPE
Final stats: $ISSUES_FOUND found, $ISSUES_FIXED fixed" \
    '{"decision": "block", "reason": $reason}'
  exit 0
fi

# Exploration exhaustion - stop after 3 consecutive exploration iterations with empty backlog
if [[ $EXPLORATION_STREAK -ge 3 ]]; then
  archive_state
  jq -n --arg reason "✅ Loop complete - exploration found no more work after 3 attempts.
Scope was: $SCOPE
Final stats: $ISSUES_FOUND found, $ISSUES_FIXED fixed" \
    '{"decision": "block", "reason": $reason}'
  exit 0
fi

# Increment iteration
NEXT_ITER=$((ITERATION + 1))

# Check for cycle completion signal in transcript
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // ""')
CYCLE_COMPLETED=false
if [[ -n "$TRANSCRIPT_PATH" ]] && [[ -f "$TRANSCRIPT_PATH" ]]; then
  if grep -q "<cycle_complete>" "$TRANSCRIPT_PATH" 2>/dev/null; then
    CYCLE_COMPLETED=true
  fi
fi

# Parse backlog section to check if empty
BACKLOG=$(parse_section "Backlog" 2>/dev/null || echo "")
BACKLOG_EMPTY=false
# Empty if: no content, only whitespace, or only placeholder text like "(Tasks discovered...)"
if [[ -z "$BACKLOG" ]] || [[ "$BACKLOG" =~ ^[[:space:]]*$ ]] || [[ "$BACKLOG" =~ ^[[:space:]]*\(.*\)[[:space:]]*$ ]]; then
  BACKLOG_EMPTY=true
fi

# Determine if exploration is appropriate (vs exploitation/focus)
# Explore when: cycle complete OR backlog is empty (nothing to work on)
SHOULD_EXPLORE=false
if [[ "$CYCLE_COMPLETED" == "true" ]] || [[ "$BACKLOG_EMPTY" == "true" ]]; then
  SHOULD_EXPLORE=true
fi

# Track exploration streak (consecutive exploration iterations with empty backlog)
# Resets when backlog has items (model found work to do)
if [[ "$SHOULD_EXPLORE" == "true" ]] && [[ "$BACKLOG_EMPTY" == "true" ]]; then
  NEW_EXPLORATION_STREAK=$((EXPLORATION_STREAK + 1))
else
  NEW_EXPLORATION_STREAK=0
fi

# Get rotating suggestion from presets (exploitation only - exploration uses Explore subagent)
SUGGESTION=""
if command -v python &>/dev/null; then
  SUGGESTION_JSON=$(python "$SCRIPTS_DIR/get-suggestion.py" "$PRESET" "$NEXT_ITER" 2>/dev/null || echo '{}')
  SUGGESTION=$(echo "$SUGGESTION_JSON" | jq -r '.suggestion // empty')
fi

# Detect idle state (no git changes and no state file changes)
GIT_DIFF=$(git diff --stat 2>/dev/null || echo "")
STATE_CHANGED=false
if [[ -f "$BACKUP_FILE" ]]; then
  if ! diff -q "$STATE_FILE" "$BACKUP_FILE" &>/dev/null; then
    STATE_CHANGED=true
  fi
fi

if [[ -z "$GIT_DIFF" ]] && [[ "$STATE_CHANGED" == "false" ]]; then
  NEW_IDLE_STREAK=$((IDLE_STREAK + 1))
else
  NEW_IDLE_STREAK=0
fi

# Update state file
update_sed() {
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "$@" "$STATE_FILE"
  else
    sed -i "$@" "$STATE_FILE"
  fi
}

update_sed "s/^iteration: .*/iteration: $NEXT_ITER/"
update_sed "s/^idle_streak: .*/idle_streak: $NEW_IDLE_STREAK/"
update_sed "s/^exploration_streak: .*/exploration_streak: $NEW_EXPLORATION_STREAK/"

# Build progress message
PROGRESS_MSG="📊 Progress: $ISSUES_FOUND found, $ISSUES_FIXED fixed"

# Build context reminder if present
CONTEXT_MSG=""
if [[ -n "$CONTEXT" ]] && [[ "$CONTEXT" != *"omit this section"* ]]; then
  CONTEXT_MSG="
🛠️ CONTEXT:
$CONTEXT"
fi

# Build continuation message
if [[ "$SHOULD_EXPLORE" == "true" ]]; then
  # Exploration mode - use Explore subagent to find more work
  REASON="🔄 Iteration $NEXT_ITER of $MAX_ITER
$PROGRESS_MSG

🔍 EXPLORATION MODE - Backlog empty, find more work.

Use the Task tool with subagent_type='Explore' to search for more work within scope.
Include in the prompt:
- Scope: $SCOPE
- State file: .claude/loop-state.local.md
- What to look for: issues, improvements, edge cases related to the scope

Add any findings to the Backlog section of the state file.$CONTEXT_MSG"

else
  # Exploitation mode - focus on current work
  REASON="🔄 Iteration $NEXT_ITER of $MAX_ITER
$PROGRESS_MSG

Continue working on your task.
💡 $SUGGESTION

⚠️ SCOPE: $SCOPE
Stay focused on this. If you've drifted, refocus.$CONTEXT_MSG"
fi

# Add idle warning if streak is building
if [[ $NEW_IDLE_STREAK -ge 2 ]]; then
  REASON="$REASON

⚠️ Idle streak: $NEW_IDLE_STREAK iterations without progress. Make changes or the loop will stop."
fi

# Output decision
jq -n --arg reason "$REASON" '{
  "decision": "block",
  "reason": $reason
}'
