#!/bin/bash
#
# Sequential Factorial Experiment Orchestrator
# Runs all 6 factorial experiments (C255-C260) in sequence
#
# Usage: ./run_all_factorial_experiments.sh
#
# Features:
#   - Waits for each experiment to complete before launching next
#   - Logs progress to /tmp/factorial_orchestrator.log
#   - Runs aggregation analysis after all experiments complete
#   - Fully autonomous execution
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-10-26
# Cycle: 259

set -e  # Exit on error

EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
RESULTS_DIR="$EXPERIMENTS_DIR/results"
LOG_FILE="/tmp/factorial_orchestrator.log"

# Redirect all output to log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "================================================================================"
echo "FACTORIAL EXPERIMENT ORCHESTRATOR - PAPER 3"
echo "================================================================================"
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Experiment definitions
declare -a EXPERIMENTS=(
    "cycle255_h1h2_mechanism_validation.py:C255:H1×H2"
    "cycle256_h1h4_mechanism_validation.py:C256:H1×H4"
    "cycle257_h1h5_mechanism_validation.py:C257:H1×H5"
    "cycle258_h2h4_mechanism_validation.py:C258:H2×H4"
    "cycle259_h2h5_mechanism_validation.py:C259:H2×H5"
    "cycle260_h4h5_mechanism_validation.py:C260:H4×H5"
)

# Function to run single experiment
run_experiment() {
    local exp_file="$1"
    local exp_name="$2"
    local exp_label="$3"
    local results_file="$RESULTS_DIR/$(basename "$exp_file" .py)_results.json"

    echo "--------------------------------------------------------------------------------"
    echo "[$exp_name] $exp_label"
    echo "--------------------------------------------------------------------------------"
    echo "Script: $exp_file"
    echo "Results: $results_file"
    echo "Start: $(date '+%H:%M:%S')"
    echo ""

    # Check if results already exist
    if [ -f "$results_file" ]; then
        echo "⚠️  Results file already exists. Skipping execution."
        echo "    (Delete $results_file to re-run)"
        echo ""
        return 0
    fi

    # Launch experiment
    cd "$EXPERIMENTS_DIR"
    local start_time=$(date +%s)

    if python3 "$exp_file"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local minutes=$((duration / 60))
        local seconds=$((duration % 60))

        echo ""
        echo "✅ $exp_name completed successfully"
        echo "   Runtime: ${minutes}m ${seconds}s"
        echo "   End: $(date '+%H:%M:%S')"
        echo ""
    else
        echo ""
        echo "❌ $exp_name FAILED (exit code $?)"
        echo "   End: $(date '+%H:%M:%S')"
        echo ""
        exit 1
    fi
}

# Run all experiments sequentially
total_start=$(date +%s)
completed=0

for exp_entry in "${EXPERIMENTS[@]}"; do
    IFS=':' read -r exp_file exp_name exp_label <<< "$exp_entry"
    run_experiment "$exp_file" "$exp_name" "$exp_label"
    ((completed++))
    echo "Progress: $completed/${#EXPERIMENTS[@]} experiments complete"
    echo ""
done

total_end=$(date +%s)
total_duration=$((total_end - total_start))
total_minutes=$((total_duration / 60))
total_seconds=$((total_duration % 60))

echo "================================================================================"
echo "ALL FACTORIAL EXPERIMENTS COMPLETE"
echo "================================================================================"
echo "Total experiments: ${#EXPERIMENTS[@]}"
echo "Total runtime: ${total_minutes}m ${total_seconds}s"
echo "End time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run aggregation analysis
echo "--------------------------------------------------------------------------------"
echo "SYNERGY AGGREGATION ANALYSIS"
echo "--------------------------------------------------------------------------------"
echo ""

cd "$EXPERIMENTS_DIR"
if python3 aggregate_factorial_synergies.py; then
    echo ""
    echo "✅ Aggregation analysis complete"
    echo ""
else
    echo ""
    echo "⚠️  Aggregation analysis failed (non-critical)"
    echo ""
fi

# Auto-generate publication figures
echo "--------------------------------------------------------------------------------"
echo "PUBLICATION FIGURE GENERATION"
echo "--------------------------------------------------------------------------------"
echo ""

if python3 generate_paper3_figures.py; then
    echo ""
    echo "✅ Publication figures generated"
    echo ""
else
    echo ""
    echo "⚠️  Figure generation failed (non-critical)"
    echo ""
fi

# Auto-fill Paper 3 manuscript
echo "--------------------------------------------------------------------------------"
echo "MANUSCRIPT AUTO-FILL"
echo "--------------------------------------------------------------------------------"
echo ""

if python3 auto_fill_paper3_manuscript.py; then
    echo ""
    echo "✅ Paper 3 manuscript auto-filled"
    echo ""
else
    echo ""
    echo "⚠️  Manuscript auto-fill failed (non-critical)"
    echo ""
fi

echo "================================================================================"
echo "PAPER 3 COMPLETE AUTOMATION PIPELINE FINISHED"
echo "================================================================================"
echo ""
echo "Generated outputs:"
echo "  • Aggregation: $RESULTS_DIR/paper3_factorial_synergy_summary.json"
echo "  • Synergy matrix: $RESULTS_DIR/paper3_synergy_matrix.txt"
echo "  • Results draft: $RESULTS_DIR/paper3_results_draft.md"
echo "  • Publication figures: $RESULTS_DIR/figures/"
echo "  • Manuscript: (check paper3 manuscript with filled Results section)"
echo ""
echo "Log file: $LOG_FILE"
echo ""

exit 0
