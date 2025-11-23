#!/bin/bash
#
# Batch Execution Script: C257-C260 Factorial Experiments
#
# Purpose: Execute remaining 4 factorial validation experiments sequentially
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-10-29
# Cycle: 573
# License: GPL-3.0
#
# Usage: ./run_c257_c260_batch.sh
# Expected Runtime: ~47 minutes total (11 + 12 + 13 + 11 min)
#

# Configuration
EXPERIMENT_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
RESULTS_DIR="${EXPERIMENT_DIR}/results"
LOGS_DIR="${EXPERIMENT_DIR}/logs"

# Ensure logs directory exists
mkdir -p "${LOGS_DIR}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "FACTORIAL VALIDATION BATCH EXECUTION: C257-C260"
echo "========================================================================"
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Expected duration: ~47 minutes (4 experiments)"
echo ""

# Track overall success
TOTAL_EXPERIMENTS=4
SUCCESSFUL=0
FAILED=0

# Experiment list (using optimized versions for 90× speedup)
declare -a experiments=(
    "cycle257_h1h5_optimized.py:H1×H5 (Energy Pooling × Energy Recovery):11"
    "cycle258_h2h4_optimized.py:H2×H4 (Reality Sources × Spawn Throttling):12"
    "cycle259_h2h5_optimized.py:H2×H5 (Reality Sources × Energy Recovery):13"
    "cycle260_h4h5_optimized.py:H4×H5 (Spawn Throttling × Energy Recovery):11"
)

# Execute each experiment sequentially
for i in "${!experiments[@]}"; do
    IFS=':' read -r script name duration <<< "${experiments[$i]}"
    exp_num=$((i + 257))

    echo ""
    echo "${BLUE}======================================================================${NC}"
    echo "${BLUE}[$(date '+%H:%M:%S')] Experiment $((i + 1))/$TOTAL_EXPERIMENTS: $name${NC}"
    echo "${BLUE}======================================================================${NC}"
    echo "Script: $script"
    echo "Expected duration: ~${duration} minutes"
    echo "Output log: ${LOGS_DIR}/cycle${exp_num}_execution.log"
    echo ""

    # Check if script exists
    if [ ! -f "${EXPERIMENT_DIR}/${script}" ]; then
        echo "${RED}ERROR: Script not found: ${script}${NC}"
        echo "${RED}Skipping experiment${NC}"
        FAILED=$((FAILED + 1))
        continue
    fi

    # Execute experiment
    start_time=$(date +%s)
    python3 "${EXPERIMENT_DIR}/${script}" > "${LOGS_DIR}/cycle${exp_num}_execution.log" 2>&1
    exit_code=$?
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    elapsed_min=$((elapsed / 60))
    elapsed_sec=$((elapsed % 60))

    # Check success
    if [ $exit_code -eq 0 ]; then
        # Verify results file exists
        result_file="${RESULTS_DIR}/cycle${exp_num}_h*_mechanism_validation_results.json"
        if ls $result_file 1> /dev/null 2>&1; then
            echo "${GREEN}✓ SUCCESS${NC} - Completed in ${elapsed_min}m ${elapsed_sec}s"
            SUCCESSFUL=$((SUCCESSFUL + 1))
        else
            echo "${YELLOW}⚠ WARNING${NC} - Script completed but no results file found"
            echo "  Expected: ${result_file}"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "${RED}✗ FAILED${NC} - Exit code: $exit_code"
        echo "${RED}  Check log: ${LOGS_DIR}/cycle${exp_num}_execution.log${NC}"
        FAILED=$((FAILED + 1))
    fi
done

# Final summary
echo ""
echo "========================================================================"
echo "BATCH EXECUTION SUMMARY"
echo "========================================================================"
echo "End time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Total experiments: $TOTAL_EXPERIMENTS"
echo "${GREEN}Successful: $SUCCESSFUL${NC}"
if [ $FAILED -gt 0 ]; then
    echo "${RED}Failed: $FAILED${NC}"
else
    echo "Failed: 0"
fi
echo ""

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    echo "${YELLOW}WARNING: Some experiments failed${NC}"
    echo "Review logs in: ${LOGS_DIR}/"
    exit 1
else
    echo "${GREEN}All experiments completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Analyze results: python3 ${EXPERIMENT_DIR}/aggregate_paper3_results.py"
    echo "  2. Generate figures: python3 ${EXPERIMENT_DIR}/generate_paper3_figures.py"
    echo "  3. Update Paper 3 manuscript with complete factorial data"
    exit 0
fi
