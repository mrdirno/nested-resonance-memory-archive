#!/bin/bash
#
# Pulse Monitor Launcher (Heartbeat System)
# Replaces "meta-orchestrate" / "autoclicker" logic.
#
# Usage:
#   meta-pilot          # Interactive selection
#   meta-pilot claude   # Launch Claude
#   meta-pilot gemini   # Launch Gemini
#

cd "$(dirname "$0")"

if [ "$1" == "" ]; then
    python3 pulse_monitor.py --ai auto
elif [ "$1" == "claude" ]; then
    python3 pulse_monitor.py --ai claude
elif [ "$1" == "gemini" ]; then
    python3 pulse_monitor.py --ai gemini
else
    echo "Usage: $0 [claude|gemini]"
    exit 1
fi
