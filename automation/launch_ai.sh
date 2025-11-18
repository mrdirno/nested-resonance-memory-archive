#!/bin/bash
#
# Quick launcher for meta-orchestration
#
# Usage:
#   ./launch_ai.sh          # Interactive selection
#   ./launch_ai.sh claude   # Launch Claude
#   ./launch_ai.sh gemini   # Launch Gemini
#
# Keyboard Shortcut (macOS):
#   System Preferences → Keyboard → Shortcuts → App Shortcuts
#   Add: Cmd+Shift+M → /Volumes/dual/DUALITY-ZERO-V2/automation/launch_ai.sh
#

cd "$(dirname "$0")"

if [ "$1" == "" ]; then
    python3 meta_orchestrate.py --ai auto
elif [ "$1" == "claude" ]; then
    python3 meta_orchestrate.py --ai claude
elif [ "$1" == "gemini" ]; then
    python3 meta_orchestrate.py --ai gemini
else
    echo "Usage: $0 [claude|gemini]"
    exit 1
fi
