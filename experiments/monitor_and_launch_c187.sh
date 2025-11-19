#!/bin/bash
#
# Automatic C186→C187 Handoff Monitor
#
# Purpose: Monitor C186 completion and automatically launch C187
#
# This script embodies the zero-delay pattern:
# - Continuous monitoring during C186 execution
# - Immediate C187 launch upon C186 completion
# - No manual intervention required for campaign continuity
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-11-05
# Cycle: 1030
# License: GPL-3.0
#
# Co-Authored-By: Claude <noreply@anthropic.com>

set -e

# Configuration
C186_PID=33600
C186_RESULTS="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json"
C187_SCRIPT="/Volumes/dual/DUALITY-ZERO-V2/experiments/cycle187_network_structure_effects.py"
C187_LOG="/tmp/c187_output.log"
EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
CHECK_INTERVAL=60  # seconds

echo "================================================================================"
echo "C186→C187 AUTOMATIC HANDOFF MONITOR"
echo "================================================================================"
echo ""
echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "C186 PID: $C186_PID"
echo "C187 Script: $C187_SCRIPT"
echo "Check Interval: ${CHECK_INTERVAL}s"
echo ""
echo "Monitoring C186 completion..."
echo ""

# Function to check if C186 is complete
check_c186_complete() {
    # Method 1: Check if process exists
    if ! ps -p $C186_PID > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] C186 process terminated"
        return 0
    fi

    # Method 2: Check if results file exists and has 10 experiments
    if [ -f "$C186_RESULTS" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$C186_RESULTS')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")

        if [ "$exp_count" -eq 10 ]; then
            echo "[$(date '+%H:%M:%S')] ✅ C186 COMPLETE: $exp_count/10 experiments"
            return 0
        else
            echo "[$(date '+%H:%M:%S')] C186 running: $exp_count/10 experiments complete"
        fi
    fi

    return 1
}

# Function to launch C187
launch_c187() {
    echo ""
    echo "================================================================================"
    echo "LAUNCHING C187: NETWORK STRUCTURE EFFECTS"
    echo "================================================================================"
    echo ""
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Script: $C187_SCRIPT"
    echo "Log: $C187_LOG"
    echo "Expected: 30 experiments, ~5 hours"
    echo ""

    cd "$EXPERIMENTS_DIR"
    nohup python3 -u "$C187_SCRIPT" > "$C187_LOG" 2>&1 &
    local c187_pid=$!

    echo "✅ C187 launched successfully (PID: $c187_pid)"
    echo ""
    echo "Monitor C187 progress:"
    echo "  tail -f $C187_LOG"
    echo ""
    echo "================================================================================"
    echo "HANDOFF COMPLETE: C186 → C187"
    echo "================================================================================"
}

# Main monitoring loop
while true; do
    if check_c186_complete; then
        # C186 complete, launch C187
        sleep 5  # Brief pause to ensure clean state
        launch_c187
        exit 0
    fi

    # Wait before next check
    sleep $CHECK_INTERVAL
done
