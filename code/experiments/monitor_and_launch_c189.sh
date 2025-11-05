#!/bin/bash
#
# Automatic C188→C189 Handoff Monitor
#
# Purpose: Monitor C188 completion and automatically launch C189
#
# This script embodies the zero-delay pattern:
# - Continuous monitoring during C188 execution
# - Immediate C189 launch upon C188 completion
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
C188_RESULTS="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json"
C189_SCRIPT="/Volumes/dual/DUALITY-ZERO-V2/experiments/cycle189_burst_clustering.py"
C189_LOG="/tmp/c189_output.log"
EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
CHECK_INTERVAL=60  # seconds

echo "================================================================================"
echo "C188→C189 AUTOMATIC HANDOFF MONITOR"
echo "================================================================================"
echo ""
echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "C188 Results: $C188_RESULTS"
echo "C189 Script: $C189_SCRIPT"
echo "Check Interval: ${CHECK_INTERVAL}s"
echo ""
echo "Monitoring C188 completion..."
echo ""

# Function to check if C188 is complete
check_c188_complete() {
    # Check if results file exists and has 40 experiments
    if [ -f "$C188_RESULTS" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$C188_RESULTS')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")

        if [ "$exp_count" -eq 40 ]; then
            echo "[$(date '+%H:%M:%S')] ✅ C188 COMPLETE: $exp_count/40 experiments"
            return 0
        else
            echo "[$(date '+%H:%M:%S')] C188 running: $exp_count/40 experiments complete"
        fi
    else
        echo "[$(date '+%H:%M:%S')] C188 running: results file not yet created"
    fi

    return 1
}

# Function to launch C189
launch_c189() {
    echo ""
    echo "================================================================================"
    echo "LAUNCHING C189: BURST CLUSTERING"
    echo "================================================================================"
    echo ""
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Script: $C189_SCRIPT"
    echo "Log: $C189_LOG"
    echo "Expected: 100 experiments, ~16.7 hours"
    echo ""

    cd "$EXPERIMENTS_DIR"
    nohup python3 -u "$C189_SCRIPT" > "$C189_LOG" 2>&1 &
    local c189_pid=$!

    echo "✅ C189 launched successfully (PID: $c189_pid)"
    echo ""
    echo "Monitor C189 progress:"
    echo "  tail -f $C189_LOG"
    echo ""
    echo "================================================================================"
    echo "HANDOFF COMPLETE: C188 → C189"
    echo "================================================================================"
}

# Main monitoring loop
while true; do
    if check_c188_complete; then
        # C188 complete, launch C189
        sleep 5  # Brief pause to ensure clean state
        launch_c189
        exit 0
    fi

    # Wait before next check
    sleep $CHECK_INTERVAL
done
