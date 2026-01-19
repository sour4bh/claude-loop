#!/usr/bin/env python3
"""Build command files from template + presets."""

import tomllib
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
SRC_DIR = PLUGIN_ROOT / "src"
COMMANDS_DIR = PLUGIN_ROOT / "commands"
USER_PRESETS_PATH = Path.home() / ".config" / "claude-loop" / "presets.toml"


def load_presets() -> dict:
    """Load built-in and user presets."""
    presets = {}
    builtin_path = SRC_DIR / "presets.toml"
    if builtin_path.exists():
        with open(builtin_path, "rb") as f:
            presets.update(tomllib.load(f))
    if USER_PRESETS_PATH.exists():
        with open(USER_PRESETS_PATH, "rb") as f:
            presets.update(tomllib.load(f))
        print(f"Loaded user presets from {USER_PRESETS_PATH}")
    return presets


def load_template() -> str:
    return (SRC_DIR / "template.md").read_text()


PRESET_GUIDANCE = {
    "ui": "Check browser, desktop/mobile, loading/error states, interactive elements.",
    "code-quality": "Run type checker, simplify patterns, check error handling, verify naming.",
    "docs": "Check README, verify examples work, document public APIs, update install instructions.",
    "review": "Check logic errors, security, error handling, test coverage.",
}


def generate_command(preset_key: str, preset_data: dict, template: str) -> str:
    description = preset_data.get("description", f"{preset_key} loop")
    is_generic = preset_key == "generic"

    work = "Execute the task. Document progress in state file. When done, explore related improvements."
    if preset_key in PRESET_GUIDANCE:
        work += f"\n\n**{preset_key.replace('-', ' ').title()}:** {PRESET_GUIDANCE[preset_key]}"

    replacements = {
        "{{PRESET_KEY}}": preset_key,
        "{{PRESET_NAME}}": preset_key.replace("-", " ").title(),
        "{{DESCRIPTION}}": description,
        "{{SUGGESTIONS_PARAM}}": "- `--suggestions <preset>`: Override suggestions" if is_generic else "",
        "{{WORK_INSTRUCTIONS}}": work,
    }

    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content


def build_all():
    COMMANDS_DIR.mkdir(exist_ok=True)
    presets = load_presets()
    template = load_template()
    print(f"Building commands for {len(presets)} presets...")

    for preset_key, preset_data in presets.items():
        content = generate_command(preset_key, preset_data, template)
        filename = "loop.md" if preset_key == "generic" else f"{preset_key}.md"
        (COMMANDS_DIR / filename).write_text(content)
        print(f"  Generated: {filename}")

    print(f"\nGenerated {len(presets)} command files in {COMMANDS_DIR}")


if __name__ == "__main__":
    build_all()
