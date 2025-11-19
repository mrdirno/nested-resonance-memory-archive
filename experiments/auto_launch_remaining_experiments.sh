#!/bin/bash
#
# Auto-Launch Remaining Factorial Experiments
# Continuously monitors C255 completion and immediately launches C256-C260 orchestrator
#
# Usage: ./auto_launch_remaining_experiments.sh &
#        (runs in background, monitors C255, auto-launches when ready)
#
# Features:
#   - Zero-delay handoff from C255 → C256-C260
#   - Logs all activity to /tmp/auto_launch.log
#   - Graceful handling of edge cases
#   - Autonomous operation per DUALITY-ZERO mandate
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-10-26
# Cycle: 261

set -e

EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
RESULTS_DIR="$EXPERIMENTS_DIR/results"
LOG_FILE="/tmp/auto_launch.log"
C255_RESULTS="$RESULTS_DIR/cycle255_h1h2_mechanism_validation_results.json"
ORCHESTRATOR="$EXPERIMENTS_DIR/run_all_factorial_experiments.sh"

# Redirect all output to log
exec > >(tee -a "$LOG_FILE") 2>&1

echo "================================================================================"
echo "AUTO-LAUNCH: FACTORIAL EXPERIMENT ORCHESTRATOR"
echo "================================================================================"
echo "Start: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Monitoring C255 completion..."
echo "  Results file: $C255_RESULTS"
echo "  Check interval: 30 seconds"
echo "  Orchestrator: $ORCHESTRATOR"
echo ""

# Monitor C255 completion
check_count=0
while true; do
    check_count=$((check_count + 1))

    # Check if C255 results exist
    if [ -f "$C255_RESULTS" ]; then
        echo ""
        echo "================================================================================"
        echo "✅ C255 COMPLETED - RESULTS DETECTED"
        echo "================================================================================"
        echo "Completion time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Checks performed: $check_count"
        echo ""

        # Verify results are valid JSON
        if python3 -m json.tool "$C255_RESULTS" > /dev/null 2>&1; then
            echo "✅ Results file valid JSON"

            # Display C255 summary
            echo ""
            echo "C255 H1×H2 Summary:"
            echo "  Mean populations:"
            python3 -c "
import json
with open('$C255_RESULTS', 'r') as f:
    data = json.load(f)
    sa = data['synergy_analysis']
    print(f\"    OFF-OFF: {sa['off_off']:.4f}\")
    print(f\"    ON-OFF:  {sa['on_off']:.4f}\")
    print(f\"    OFF-ON:  {sa['off_on']:.4f}\")
    print(f\"    ON-ON:   {sa['on_on']:.4f}\")
    print(f\"  Synergy: {sa['synergy']:.4f} ({sa['classification']})\")
"
            echo ""
        else
            echo "⚠️  Warning: Results file exists but may be incomplete"
            echo "   Proceeding anyway (orchestrator will handle errors)"
            echo ""
        fi

        # Launch orchestrator
        echo "--------------------------------------------------------------------------------"
        echo "LAUNCHING ORCHESTRATOR FOR C256-C260"
        echo "--------------------------------------------------------------------------------"
        echo "Script: $ORCHESTRATOR"
        echo "Launch time: $(date '+%H:%M:%S')"
        echo ""

        cd "$EXPERIMENTS_DIR"

        if [ -x "$ORCHESTRATOR" ]; then
            # Launch orchestrator
            bash "$ORCHESTRATOR"
            exit_code=$?

            echo ""
            echo "================================================================================"
            if [ $exit_code -eq 0 ]; then
                echo "✅ ORCHESTRATOR COMPLETED SUCCESSFULLY"
            else
                echo "❌ ORCHESTRATOR FAILED (exit code: $exit_code)"
            fi
            echo "================================================================================"
            echo "End: $(date '+%Y-%m-%d %H:%M:%S')"
            echo ""

            exit $exit_code
        else
            echo "❌ ERROR: Orchestrator not executable: $ORCHESTRATOR"
            echo "   Fix: chmod +x $ORCHESTRATOR"
            exit 1
        fi
    fi

    # Progress indicator (every 5 checks = 2.5 minutes)
    if [ $((check_count % 5)) -eq 0 ]; then
        elapsed_min=$((check_count / 2))
        echo "[$(date '+%H:%M:%S')] Still monitoring... (${elapsed_min} min elapsed, ${check_count} checks)"
    fi

    # Sleep before next check
    sleep 30
done
