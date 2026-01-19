---
description: Cancel the active autonomous loop
---

# Cancel Loop

1. Check for `.claude/loop-state.local.md`
2. If missing: "No active loop to cancel."
3. If exists:
   - Read state for progress summary
   - Archive to `.claude/loop-history/{timestamp}.md`
   - Delete state file
   - Report: scope, iterations, issues found/fixed, "Loop cancelled."
