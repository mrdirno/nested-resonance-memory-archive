#!/bin/bash
# AUTOMATED STOCHASTICITY INVESTIGATION COMPLETION WORKFLOW
# Cycles 235-247: V6 → Analysis → V7 → Final Analysis → Strategic Decision
#
# This script:
# 1. Waits for V6 completion
# 2. Runs intermediate analysis
# 3. Launches V7 validation
# 4. Waits for V7 completion
# 5. Runs final analysis
# 6. Displays strategic recommendation
#
# Date: 2025-10-26
# Cycle: 246

set -e  # Exit on error

EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
RESULTS_DIR="$EXPERIMENTS_DIR/results"

echo "================================================================================"
echo "STOCHASTICITY INVESTIGATION: AUTOMATED COMPLETION WORKFLOW"
echo "================================================================================"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Step 1: Wait for V6 completion
echo "[1/5] Waiting for V6 completion..."
V6_RESULT="$RESULTS_DIR/cycle177_v6_measurement_noise_validation_results.json"

while [ ! -f "$V6_RESULT" ]; do
    echo "  V6 still running: $(date +%H:%M:%S)"
    sleep 60
done

echo "✓ V6 COMPLETED: $(date +%H:%M:%S)"
echo "  Results: $V6_RESULT"
echo ""

# Step 2: Run intermediate analysis (V5 + V6)
echo "[2/5] Running intermediate analysis (V5+V6)..."
cd "$EXPERIMENTS_DIR"
python3 analyze_stochasticity_investigation.py > /tmp/v6_analysis.log 2>&1
echo "✓ Intermediate analysis complete"
echo "  Report: $EXPERIMENTS_DIR/STOCHASTICITY_INVESTIGATION_ANALYSIS.md"
echo ""

# Step 3: Launch V7 validation
echo "[3/5] Launching V7 validation (10% noise)..."
cd "$EXPERIMENTS_DIR"
python3 cycle177_v7_increased_noise_validation.py > /tmp/v7_run.log 2>&1 &
V7_PID=$!
echo "✓ V7 launched (PID: $V7_PID)"
echo "  Started: $(date +%H:%M:%S)"
echo ""

# Step 4: Wait for V7 completion
echo "[4/5] Waiting for V7 completion..."
V7_RESULT="$RESULTS_DIR/cycle177_v7_increased_noise_validation_results.json"

while [ ! -f "$V7_RESULT" ]; do
    echo "  V7 still running: $(date +%H:%M:%S)"
    sleep 60
done

echo "✓ V7 COMPLETED: $(date +%H:%M:%S)"
echo "  Results: $V7_RESULT"
echo ""

# Step 5: Run final analysis (V5 + V6 + V7)
echo "[5/5] Running final analysis (V5+V6+V7)..."
cd "$EXPERIMENTS_DIR"
python3 analyze_stochasticity_investigation.py

echo ""
echo "================================================================================"
echo "STOCHASTICITY INVESTIGATION: WORKFLOW COMPLETE"
echo "================================================================================"
echo "Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Review strategic recommendation in:"
echo "  $EXPERIMENTS_DIR/STOCHASTICITY_INVESTIGATION_ANALYSIS.md"
echo ""
echo "Next Actions:"
echo "  1. Review analysis report"
echo "  2. Execute strategic decision (ACCEPT_DETERMINISM or ATTEMPT_V8)"
echo "  3. Update Paper 3 experiments accordingly"
echo "  4. Document final conclusion in STOCHASTICITY_INVESTIGATION"
echo ""
echo "================================================================================"
