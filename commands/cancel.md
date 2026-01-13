---
description: Cancel the active autonomous loop
---

# Cancel Loop

Stop the currently running autonomous loop.

## Your Task

1. Check if a loop is active by looking for `.claude/loop-state.local.md`

2. If no state file exists:
   - Tell the user: "No active loop to cancel."

3. If state file exists:
   - Read the state file to get current progress
   - Archive it to `.claude/loop-history/{timestamp}.md`
   - Delete the state file
   - Report to the user:
     - What the scope was
     - How many iterations completed
     - Issues found/fixed (if tracked)
     - "Loop cancelled successfully."

## Important

- The stop hook checks for the state file's existence
- Deleting the state file stops the loop on the next iteration
- Always archive before deleting so work isn't lost
