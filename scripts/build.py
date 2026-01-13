#!/usr/bin/env python3
"""
Build script for claude-loop plugin.
Generates command files from template + presets.
"""

import tomllib
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parent.parent
SRC_DIR = PLUGIN_ROOT / "src"
COMMANDS_DIR = PLUGIN_ROOT / "commands"
USER_PRESETS_PATH = Path.home() / ".config" / "claude-loop" / "presets.toml"


def load_presets() -> dict:
    """Load built-in and user presets, user overrides built-in."""
    presets = {}

    # Load built-in presets
    builtin_path = SRC_DIR / "presets.toml"
    if builtin_path.exists():
        with open(builtin_path, "rb") as f:
            presets.update(tomllib.load(f))

    # Load user presets (override built-in)
    if USER_PRESETS_PATH.exists():
        with open(USER_PRESETS_PATH, "rb") as f:
            presets.update(tomllib.load(f))
        print(f"Loaded user presets from {USER_PRESETS_PATH}")

    return presets


def load_template() -> str:
    """Load the base template."""
    template_path = SRC_DIR / "template.md"
    return template_path.read_text()


def generate_command(preset_key: str, preset_data: dict, template: str) -> str:
    """Generate a command file for a preset."""
    description = preset_data.get("description", f"{preset_key} loop")
    suggestions = preset_data.get("suggestions", [])

    # Determine if this is the generic preset
    is_generic = preset_key == "generic"

    # Build replacements
    replacements = {
        "{{PRESET_KEY}}": preset_key,
        "{{PRESET_NAME}}": preset_key.replace("-", " ").title(),
        "{{DESCRIPTION}}": description,
        "{{MODE}}": "discovery",  # Default mode
    }

    # Generic preset can use --suggestions to override
    if is_generic:
        replacements["{{SUGGESTIONS_PARAM}}"] = "- **--suggestions <preset>**: Override suggestion preset"
    else:
        replacements["{{SUGGESTIONS_PARAM}}"] = ""

    # Task mode fields for state file
    replacements["{{TASK_MODE_FIELDS}}"] = """task_started_at: 1
issues_found: 0
issues_fixed: 0"""

    # Backlog initialization
    replacements["{{BACKLOG_INIT}}"] = "(Tasks discovered but not yet addressed)"

    # Work instructions based on preset
    work_instructions = generate_work_instructions(preset_key, suggestions)
    replacements["{{WORK_INSTRUCTIONS}}"] = work_instructions

    # Apply replacements
    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def generate_work_instructions(preset_key: str, suggestions: list) -> str:
    """Generate preset-specific work instructions."""
    base = """Execute the task from the prompt:
- When you complete something, look for the next thing to do
- Document findings and progress in the state file
- If the initial task is done, explore related improvements"""

    if preset_key == "ui":
        return base + """

**UI-specific guidance:**
- Open pages in browser to verify visual appearance
- Check both desktop and mobile viewports
- Verify loading, error, and empty states
- Test interactive elements (buttons, forms, links)"""

    elif preset_key == "code-quality":
        return base + """

**Code quality guidance:**
- Run type checker to find issues
- Look for patterns that could be simplified
- Check for consistent error handling
- Verify naming follows conventions"""

    elif preset_key == "docs":
        return base + """

**Documentation guidance:**
- Check README is up to date
- Verify code examples actually work
- Look for undocumented public APIs
- Ensure install/setup instructions are current"""

    elif preset_key == "review":
        return base + """

**Code review guidance:**
- Look for logic errors and edge cases
- Check security implications
- Verify error handling is complete
- Ensure tests cover the changes"""

    return base


def build_all():
    """Build all command files."""
    COMMANDS_DIR.mkdir(exist_ok=True)

    presets = load_presets()
    template = load_template()

    print(f"Building commands for {len(presets)} presets...")

    for preset_key, preset_data in presets.items():
        # Generate command content
        content = generate_command(preset_key, preset_data, template)

        # Determine filename
        if preset_key == "generic":
            filename = "loop.md"
        else:
            filename = f"{preset_key}.md"

        # Write command file
        output_path = COMMANDS_DIR / filename
        output_path.write_text(content)
        print(f"  Generated: {filename}")

    print(f"\nGenerated {len(presets)} command files in {COMMANDS_DIR}")


if __name__ == "__main__":
    build_all()
