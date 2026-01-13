#!/usr/bin/env python3
"""
Get rotating suggestions from presets for claude-loop.
Fallback when Haiku AI is not available.
"""

import json
import sys
import tomllib
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent
SRC_DIR = PLUGIN_ROOT / "src"
USER_PRESETS_PATH = Path.home() / ".config" / "claude-loop" / "presets.toml"


def load_presets() -> dict:
    """Load built-in and user presets."""
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

    return presets


def get_suggestion(preset: str, iteration: int) -> dict:
    """Get a rotating exploitation suggestion for the given preset and iteration."""
    presets = load_presets()

    if preset not in presets:
        preset = "generic"

    preset_data = presets.get(preset, {})
    suggestions = preset_data.get("exploitation", [])

    # Fallback to combined suggestions if exploitation empty
    if not suggestions:
        suggestions = preset_data.get("suggestions", [])

    # Hardcoded fallback if preset has no suggestions
    if not suggestions:
        suggestions = [
            "Complete your current task before moving on",
            "Check your backlog and pick the highest priority item",
            "Verify your recent changes actually work",
        ]

    # Rotate through suggestions based on iteration
    index = iteration % len(suggestions)
    suggestion = suggestions[index]

    return {
        "preset": preset,
        "suggestion": suggestion,
        "suggestion_index": index,
        "total_suggestions": len(suggestions),
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(
            json.dumps(
                {"error": True, "message": "Usage: get-suggestion.py <preset> <iteration>"}
            )
        )
        sys.exit(1)

    preset = sys.argv[1]
    try:
        iteration = int(sys.argv[2])
    except ValueError:
        print(json.dumps({"error": True, "message": "Iteration must be a number"}))
        sys.exit(1)

    result = get_suggestion(preset, iteration)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
