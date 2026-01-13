#!/usr/bin/env python3
"""
Haiku-powered analysis for claude-loop iterations.
Analyzes state file + git diff to generate smart continuation prompts.
"""

import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

HAIKU_MODEL = "claude-3-haiku-20240307"


def get_git_diff() -> str:
    """Get git diff for current changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # Fallback to unstaged changes
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def parse_state_file(content: str) -> dict:
    """Parse state file with defensive fallbacks."""
    state = {
        "iteration": 1,
        "max_iterations": 50,
        "mode": "discovery",
        "scope": "unknown",
        "issues_found": 0,
        "issues_fixed": 0,
        "current_focus": "",
        "backlog": [],
        "completed": [],
    }

    # Try to extract frontmatter values
    patterns = {
        "iteration": r"iteration:\s*(\d+)",
        "max_iterations": r"max_iterations:\s*(\d+)",
        "mode": r"mode:\s*(\w+)",
        "scope": r"scope:\s*(.+)",
        "issues_found": r"issues_found:\s*(\d+)",
        "issues_fixed": r"issues_fixed:\s*(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1).strip()
            if key in ("iteration", "max_iterations", "issues_found", "issues_fixed"):
                state[key] = int(value)
            else:
                state[key] = value

    # Extract current focus section
    focus_match = re.search(
        r"## Current Focus\n(.+?)(?=\n##|\Z)", content, re.DOTALL
    )
    if focus_match:
        state["current_focus"] = focus_match.group(1).strip()

    # Extract backlog items
    backlog_match = re.search(r"## Backlog\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if backlog_match:
        items = re.findall(r"- \[ \] (.+)", backlog_match.group(1))
        state["backlog"] = items

    # Extract completed items
    completed_match = re.search(r"## Completed\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if completed_match:
        items = re.findall(r"- \[x\] (.+)", completed_match.group(1))
        state["completed"] = items

    return state


def call_haiku(prompt: str) -> dict | None:
    """Call Haiku API. Returns None if unavailable."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse JSON from response
        text = response.content[0].text
        # Try to extract JSON from the response
        json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None

    except ImportError:
        logger.warning("anthropic package not installed")
        return None
    except Exception as e:
        logger.warning(f"Haiku API call failed: {e}")
        return None


def analyze_iteration(state_content: str, git_diff: str, scope: str) -> dict:
    """Analyze iteration using Haiku."""
    prompt = f"""Analyze this coding loop iteration briefly.

## Scope
{scope}

## State File
{state_content[:2000]}

## Git Changes
{git_diff[:1000] if git_diff else "(no changes detected)"}

Based on the state and changes:
1. What work appears complete?
2. What should be the next focus?
3. Is the work aligned with the scope?

Return ONLY valid JSON (no markdown):
{{"suggested_next_focus": "specific action", "progress_status": "progressing|stuck|idle", "continuation_prompt": "1-2 sentence prompt", "scope_aligned": true}}"""

    result = call_haiku(prompt)
    if result:
        return result

    # Fallback: basic analysis without AI
    return {
        "suggested_next_focus": None,
        "progress_status": "unknown",
        "continuation_prompt": None,
        "scope_aligned": True,
    }


def check_idle_signals(
    state_before: dict, state_after: dict, git_diff: str
) -> dict:
    """Check multiple signals to determine if truly idle."""
    signals = {
        "state_changed": state_before != state_after,
        "git_changed": bool(git_diff.strip()),
        "focus_changed": state_before.get("current_focus") != state_after.get("current_focus"),
        "issues_changed": (
            state_before.get("issues_found", 0) != state_after.get("issues_found", 0)
            or state_before.get("issues_fixed", 0) != state_after.get("issues_fixed", 0)
        ),
        "backlog_changed": state_before.get("backlog", []) != state_after.get("backlog", []),
        "completed_changed": state_before.get("completed", []) != state_after.get("completed", []),
    }

    is_idle = not any(signals.values())

    return {
        "is_idle": is_idle,
        "signals": signals,
    }


def main():
    """Main entry point. Reads state file path from argv or stdin."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": True, "message": "Usage: analyze.py <state_file_path>"}))
        sys.exit(1)

    state_path = Path(sys.argv[1])
    if not state_path.exists():
        print(json.dumps({"error": True, "message": f"State file not found: {state_path}"}))
        sys.exit(1)

    state_content = state_path.read_text()
    state = parse_state_file(state_content)
    git_diff = get_git_diff()

    analysis = analyze_iteration(state_content, git_diff, state.get("scope", ""))

    # Build output
    output = {
        "analysis": analysis,
        "state": {
            "iteration": state["iteration"],
            "max_iterations": state["max_iterations"],
            "mode": state["mode"],
            "issues_found": state["issues_found"],
            "issues_fixed": state["issues_fixed"],
        },
        "has_git_changes": bool(git_diff.strip()),
        "haiku_available": analysis.get("continuation_prompt") is not None,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
