#!/bin/bash
# Monitor V6a campaign completion and trigger analysis
# Author: Aldrin Payopay (aldrin.gdf@gmail.com)
# Co-Authored-By: Claude <noreply@anthropic.com>
# Date: 2025-11-16
# Cycle: 1375

RESULTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
ANALYSIS_SCRIPT="/Volumes/dual/DUALITY-ZERO-V2/analysis/aggregate_v6a_results.py"
EXPECTED_COUNT=50
CHECK_INTERVAL=30  # seconds

echo "V6a Campaign Completion Monitor"
echo "================================"
echo "Expected experiments: $EXPECTED_COUNT"
echo "Check interval: ${CHECK_INTERVAL}s"
echo ""

while true; do
    # Count completed experiments
    CURRENT_COUNT=$(ls -1 "$RESULTS_DIR"/c186_v6a_HIERARCHICAL_*.json 2>/dev/null | wc -l | tr -d ' ')

    # Get timestamp
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

    echo "[$TIMESTAMP] Progress: $CURRENT_COUNT/$EXPECTED_COUNT ($(( CURRENT_COUNT * 100 / EXPECTED_COUNT ))%)"

    # Check if complete
    if [ "$CURRENT_COUNT" -ge "$EXPECTED_COUNT" ]; then
        echo ""
        echo "================================"
        echo "V6a CAMPAIGN COMPLETE!"
        echo "================================"
        echo "Total experiments: $CURRENT_COUNT"
        echo ""

        # Verify process finished
        if ps -p 7380 > /dev/null 2>&1; then
            echo "Campaign process (PID 7380) still running, waiting 30s..."
            sleep 30
        fi

        echo "Launching analysis..."
        python3 "$ANALYSIS_SCRIPT"

        echo ""
        echo "Analysis complete. Monitor exiting."
        exit 0
    fi

    # Sleep until next check
    sleep "$CHECK_INTERVAL"
done
