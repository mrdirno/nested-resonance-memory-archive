#!/bin/bash
#
# Automatic C187→C188 Handoff Monitor
#
# Purpose: Monitor C187 completion and automatically launch C188
#
# This script embodies the zero-delay pattern:
# - Continuous monitoring during C187 execution
# - Immediate C188 launch upon C187 completion
# - No manual intervention required for campaign continuity
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-11-05
# Cycle: 1031
# License: GPL-3.0
#
# Co-Authored-By: Claude <noreply@anthropic.com>

set -e

# Configuration
C187_RESULTS="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json"
C188_SCRIPT="/Volumes/dual/DUALITY-ZERO-V2/experiments/cycle188_memory_effects.py"
C188_LOG="/tmp/c188_output.log"
EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
CHECK_INTERVAL=60  # seconds

echo "================================================================================"
echo "C187→C188 AUTOMATIC HANDOFF MONITOR"
echo "================================================================================"
echo ""
echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "C187 Results: $C187_RESULTS"
echo "C188 Script: $C188_SCRIPT"
echo "Check Interval: ${CHECK_INTERVAL}s"
echo ""
echo "Monitoring C187 completion..."
echo ""

# Function to check if C187 is complete
check_c187_complete() {
    # Check if results file exists and has 30 experiments
    if [ -f "$C187_RESULTS" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$C187_RESULTS')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")

        if [ "$exp_count" -eq 30 ]; then
            echo "[$(date '+%H:%M:%S')] ✅ C187 COMPLETE: $exp_count/30 experiments"
            return 0
        else
            echo "[$(date '+%H:%M:%S')] C187 running: $exp_count/30 experiments complete"
        fi
    else
        echo "[$(date '+%H:%M:%S')] C187 running: results file not yet created"
    fi

    return 1
}

# Function to launch C188
launch_c188() {
    echo ""
    echo "================================================================================"
    echo "LAUNCHING C188: MEMORY EFFECTS"
    echo "================================================================================"
    echo ""
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Script: $C188_SCRIPT"
    echo "Log: $C188_LOG"
    echo "Expected: 40 experiments, ~6.7 hours"
    echo ""

    cd "$EXPERIMENTS_DIR"
    nohup python3 -u "$C188_SCRIPT" > "$C188_LOG" 2>&1 &
    local c188_pid=$!

    echo "✅ C188 launched successfully (PID: $c188_pid)"
    echo ""
    echo "Monitor C188 progress:"
    echo "  tail -f $C188_LOG"
    echo ""
    echo "================================================================================"
    echo "HANDOFF COMPLETE: C187 → C188"
    echo "================================================================================"
}

# Main monitoring loop
while true; do
    if check_c187_complete; then
        # C187 complete, launch C188
        sleep 5  # Brief pause to ensure clean state
        launch_c188
        exit 0
    fi

    # Wait before next check
    sleep $CHECK_INTERVAL
done
