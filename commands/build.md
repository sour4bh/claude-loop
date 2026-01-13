---
description: Rebuild loop commands from presets
---

# Build Loop Commands

Regenerate command files from the template and preset definitions.

## Your Task

1. Run the build script:
   ```bash
   python ~/.claude/plugins/claude-loop/scripts/build.py
   ```

2. Report results to user:
   - Number of commands generated
   - Any user presets loaded from `~/.config/claude-loop/presets.toml`
   - Any errors encountered

## When to Use

Run this command after:
- Adding custom presets to `~/.config/claude-loop/presets.toml`
- Modifying `src/template.md` or `src/presets.toml`
- Plugin updates

## Custom Presets

Users can add their own presets at `~/.config/claude-loop/presets.toml`:

```toml
[security]
description = "Security audit"
suggestions = [
  "Check for SQL injection vulnerabilities",
  "Look for XSS attack vectors",
  "Verify authentication flows",
]
```

After adding, run `/loop:build` to generate the new `/loop:security` command.
