#!/usr/bin/env python3
"""
Meta-Orchestration Automation Tool

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0

PURPOSE:
--------
Cross-compatible AI assistant launcher for DUALITY-ZERO project.
Supports both Claude CLI and Gemini CLI with the same constitution.

USAGE:
------
python3 meta_orchestrate.py --ai claude
python3 meta_orchestrate.py --ai gemini
python3 meta_orchestrate.py --ai auto  # Auto-detect or prompt

KEYBOARD SHORTCUT:
------------------
Cmd+Shift+M → Launch meta-orchestrator (set in system preferences)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Project root
PROJECT_ROOT = Path("/Volumes/dual/DUALITY-ZERO-V2")
GIT_REPO = Path("/Users/aldrinpayopay/nested-resonance-memory-archive")

# Constitution file (AI-agnostic)
CONSTITUTION_FILE = GIT_REPO / "CLAUDE.md"

# AI CLI commands
CLAUDE_CLI = "claude"
GEMINI_CLI = "gemini"

# Default AI (if --ai not specified)
DEFAULT_AI = "claude"

# Permissionless mode configuration
PERMISSIONLESS_TOOLS = [
    "Bash(cd:*)",
    "Bash(unzip:*)",
    "Bash(rm:*)",
    "Bash(mkdir:*)",
    "Bash(mv:*)",
    "Bash(cp:*)",
    "Bash(chmod:*)",
    "Bash(source:*)",
    "Bash(echo:*)",
    f"Read({PROJECT_ROOT}/**)",
    f"Read({GIT_REPO}/**)",
    "Bash(python3:*)",
]

# ============================================================================
# AI ASSISTANT DETECTION
# ============================================================================

def check_ai_available(ai_name):
    """Check if AI CLI is available."""
    try:
        result = subprocess.run(
            [ai_name, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def detect_available_ais():
    """Detect which AI CLIs are installed."""
    available = []

    if check_ai_available(CLAUDE_CLI):
        available.append("claude")

    if check_ai_available(GEMINI_CLI):
        available.append("gemini")

    return available


# ============================================================================
# CONSTITUTION LOADING
# ============================================================================

def load_constitution():
    """Load the AI-agnostic constitution."""
    if not CONSTITUTION_FILE.exists():
        print(f"❌ Constitution file not found: {CONSTITUTION_FILE}")
        sys.exit(1)

    with open(CONSTITUTION_FILE, 'r') as f:
        constitution = f.read()

    return constitution


def create_session_message(constitution, ai_name):
    """Create the initial session message for the AI assistant."""

    timestamp = datetime.now().isoformat()
    cycle_num = get_current_cycle()

    message = f"""📢 **CUSTOM PRIORITY MESSAGE:**
{constitution}

================================================================================

**REFERENCE FILES:**
- Constitution: `/Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md`
- Meta Objectives: `/Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md`
- Workspace: `/Volumes/dual/DUALITY-ZERO-V2/`

================================================================================

*DUALITY-ZERO-V2 Meta-Orchestration System*
*Cycle #{cycle_num} | {timestamp}*
*Autonomous Hybrid Intelligence - Continuous Operation*
*AI Assistant: {ai_name.upper()}*

Please address this message and continue with your tasks.
"""

    return message


def get_current_cycle():
    """Estimate current cycle number from summaries."""
    summaries_dir = PROJECT_ROOT / "archive" / "summaries"

    if not summaries_dir.exists():
        return 1400  # Default to recent cycle

    # Find highest cycle number in summaries
    max_cycle = 1400
    for summary_file in summaries_dir.glob("CYCLE*.md"):
        try:
            cycle_num = int(summary_file.stem.split("CYCLE")[1].split("_")[0])
            max_cycle = max(max_cycle, cycle_num)
        except (IndexError, ValueError):
            continue

    return max_cycle + 1


# ============================================================================
# AI ASSISTANT LAUNCHERS
# ============================================================================

def launch_claude(message):
    """Launch Claude CLI with constitution."""
    print("="*80)
    print("LAUNCHING CLAUDE CLI")
    print("="*80)
    print(f"\nConstitution loaded: {CONSTITUTION_FILE}")
    print(f"Permissionless tools: {len(PERMISSIONLESS_TOOLS)}")
    print(f"Working directory: {PROJECT_ROOT}")
    print("\nStarting session...")
    print("="*80)

    # Claude CLI launch
    # Note: Claude CLI configuration handled via ~/.claude/config.json
    # Constitution sent as initial message

    try:
        subprocess.run(
            [CLAUDE_CLI],
            cwd=str(PROJECT_ROOT),
            env={**os.environ},
            input=message.encode(),
            timeout=None
        )
    except KeyboardInterrupt:
        print("\n\n✓ Claude session ended")
    except Exception as e:
        print(f"\n❌ Error launching Claude: {e}")


def launch_gemini(message):
    """Launch Gemini CLI with constitution and permissionless mode."""
    print("="*80)
    print("LAUNCHING GEMINI CLI (PERMISSIONLESS MODE)")
    print("="*80)
    print(f"\nConstitution loaded: {CONSTITUTION_FILE}")
    print(f"Permissionless tools: {len(PERMISSIONLESS_TOOLS)}")
    print(f"Working directory: {PROJECT_ROOT}")
    print(f"YOLO mode: ENABLED (auto-approve all tools)")
    print("\nStarting session...")
    print("="*80)

    # Gemini CLI launch with YOLO mode (permissionless)
    # --yolo: Automatically accept all actions (equivalent to Claude permissionless)
    # --approval-mode yolo: Same as --yolo but explicit
    # Constitution sent as initial message via stdin

    try:
        # Launch Gemini with permissionless mode enabled
        subprocess.run(
            [GEMINI_CLI, "--yolo"],  # Enable permissionless mode
            cwd=str(PROJECT_ROOT),
            env={**os.environ},
            input=message.encode(),
            timeout=None
        )
    except KeyboardInterrupt:
        print("\n\n✓ Gemini session ended")
    except Exception as e:
        print(f"\n❌ Error launching Gemini: {e}")


# ============================================================================
# AI SELECTION
# ============================================================================

def select_ai_interactive(available_ais):
    """Interactively select AI if multiple are available."""
    if not available_ais:
        print("❌ No AI assistants available!")
        print("\nInstall one of:")
        print("  - Claude CLI: https://claude.ai/cli")
        print("  - Gemini CLI: npm install -g @google/gemini-cli")
        sys.exit(1)

    if len(available_ais) == 1:
        return available_ais[0]

    print("\n" + "="*80)
    print("SELECT AI ASSISTANT")
    print("="*80)
    print("\nAvailable:")
    for i, ai in enumerate(available_ais, 1):
        print(f"  [{i}] {ai.upper()}")

    while True:
        try:
            choice = input(f"\nSelect AI [1-{len(available_ais)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(available_ais):
                return available_ais[idx]
            else:
                print(f"Please enter a number between 1 and {len(available_ais)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled")
            sys.exit(0)


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Main orchestration entry point."""

    parser = argparse.ArgumentParser(
        description="Meta-Orchestration: Launch Claude or Gemini CLI with DUALITY-ZERO constitution"
    )
    parser.add_argument(
        "--ai",
        choices=["claude", "gemini", "auto"],
        default="auto",
        help="AI assistant to use (default: auto-detect or prompt)"
    )
    parser.add_argument(
        "--cycle",
        type=int,
        help="Override cycle number (default: auto-detect)"
    )

    args = parser.parse_args()

    # Detect available AIs
    available_ais = detect_available_ais()

    # Select AI
    if args.ai == "auto":
        selected_ai = select_ai_interactive(available_ais)
    else:
        if args.ai not in available_ais:
            print(f"❌ {args.ai.upper()} CLI not available")
            print(f"\nAvailable: {', '.join(available_ais) if available_ais else 'None'}")
            sys.exit(1)
        selected_ai = args.ai

    # Load constitution
    constitution = load_constitution()

    # Create session message
    message = create_session_message(constitution, selected_ai)

    # Launch selected AI
    if selected_ai == "claude":
        launch_claude(message)
    elif selected_ai == "gemini":
        launch_gemini(message)
    else:
        print(f"❌ Unknown AI: {selected_ai}")
        sys.exit(1)


if __name__ == "__main__":
    main()
