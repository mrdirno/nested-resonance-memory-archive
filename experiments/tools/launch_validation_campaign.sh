#!/bin/bash
#
# Validation Campaign Master Launcher
#
# Purpose: Orchestrate complete C186→C187→C188→C189 validation campaign
#
# This script embodies the zero-delay pattern at campaign scale:
# - Launches C186→C187 handoff monitor (if C186 running)
# - Automatically chains through all experiments
# - Total: 180 experiments, ~28 hours, zero manual intervention
#
# Usage:
#   ./launch_validation_campaign.sh [start-experiment]
#
# Examples:
#   ./launch_validation_campaign.sh       # Start from C186 (or detect current state)
#   ./launch_validation_campaign.sh C187  # Start from C187 handoff
#   ./launch_validation_campaign.sh C188  # Start from C188 handoff
#   ./launch_validation_campaign.sh C189  # Start from C189 handoff
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Date: 2025-11-05
# Cycle: 1031
# License: GPL-3.0
#
# Co-Authored-By: Claude <noreply@anthropic.com>

set -e

EXPERIMENTS_DIR="/Volumes/dual/DUALITY-ZERO-V2/experiments"
START_FROM="${1:-C186}"

echo "================================================================================"
echo "VALIDATION CAMPAIGN MASTER LAUNCHER"
echo "================================================================================"
echo ""
echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Start From: $START_FROM"
echo ""
echo "Campaign Overview:"
echo "  C186: Hierarchical Energy Dynamics (10 exp, ~6 hours)"
echo "  C187: Network Structure Effects (30 exp, ~5 hours)"
echo "  C188: Memory Effects (40 exp, ~6.7 hours)"
echo "  C189: Burst Clustering (100 exp, ~16.7 hours)"
echo "  ────────────────────────────────────────────────────"
echo "  TOTAL: 180 experiments, ~28 hours"
echo ""

# Function to detect current campaign state
detect_campaign_state() {
    local c186_results="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json"
    local c187_results="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json"
    local c188_results="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json"
    local c189_results="/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json"

    # Check C189 first (most advanced)
    if [ -f "$c189_results" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$c189_results')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")
        if [ "$exp_count" -eq 100 ]; then
            echo "C189_COMPLETE"
            return
        else
            echo "C189_RUNNING"
            return
        fi
    fi

    # Check C188
    if [ -f "$c188_results" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$c188_results')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")
        if [ "$exp_count" -eq 40 ]; then
            echo "C188_COMPLETE"
            return
        else
            echo "C188_RUNNING"
            return
        fi
    fi

    # Check C187
    if [ -f "$c187_results" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$c187_results')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")
        if [ "$exp_count" -eq 30 ]; then
            echo "C187_COMPLETE"
            return
        else
            echo "C187_RUNNING"
            return
        fi
    fi

    # Check C186
    if [ -f "$c186_results" ]; then
        local exp_count=$(python3 -c "import json; data=json.load(open('$c186_results')); print(len(data.get('experiments', [])))" 2>/dev/null || echo "0")
        if [ "$exp_count" -eq 10 ]; then
            echo "C186_COMPLETE"
            return
        else
            echo "C186_RUNNING"
            return
        fi
    fi

    echo "C186_PENDING"
}

# Detect current state if auto-starting
if [ "$START_FROM" = "C186" ]; then
    DETECTED_STATE=$(detect_campaign_state)
    echo "Detected State: $DETECTED_STATE"
    echo ""

    case "$DETECTED_STATE" in
        C189_COMPLETE)
            echo "✅ Campaign complete! All 180 experiments finished."
            exit 0
            ;;
        C189_RUNNING)
            echo "⏳ C189 already running. Nothing to launch."
            exit 0
            ;;
        C188_COMPLETE)
            START_FROM="C189"
            echo "→ Will launch C189 handoff monitor"
            ;;
        C188_RUNNING)
            START_FROM="C189"
            echo "→ Will launch C188→C189 handoff monitor"
            ;;
        C187_COMPLETE)
            START_FROM="C188"
            echo "→ Will launch C188 handoff monitor"
            ;;
        C187_RUNNING)
            START_FROM="C188"
            echo "→ Will launch C187→C188 handoff monitor"
            ;;
        C186_COMPLETE)
            START_FROM="C187"
            echo "→ Will launch C187 handoff monitor"
            ;;
        C186_RUNNING)
            START_FROM="C187"
            echo "→ Will launch C186→C187 handoff monitor"
            ;;
        C186_PENDING)
            echo "❌ C186 not started. Please launch C186 first:"
            echo "   cd $EXPERIMENTS_DIR"
            echo "   nohup python3 -u cycle186_metapopulation_hierarchical_validation.py > /tmp/c186_output.log 2>&1 &"
            exit 1
            ;;
    esac
    echo ""
fi

# Launch appropriate handoff monitor
case "$START_FROM" in
    C187)
        echo "🚀 Launching C186→C187→C188→C189 handoff chain..."
        echo ""
        nohup "$EXPERIMENTS_DIR/monitor_and_launch_c187.sh" > /tmp/handoff_c187.log 2>&1 &
        echo "   C186→C187 monitor: PID $! (log: /tmp/handoff_c187.log)"
        ;;
    C188)
        echo "🚀 Launching C187→C188→C189 handoff chain..."
        echo ""
        nohup "$EXPERIMENTS_DIR/monitor_and_launch_c188.sh" > /tmp/handoff_c188.log 2>&1 &
        echo "   C187→C188 monitor: PID $! (log: /tmp/handoff_c188.log)"
        ;;
    C189)
        echo "🚀 Launching C188→C189 handoff..."
        echo ""
        nohup "$EXPERIMENTS_DIR/monitor_and_launch_c189.sh" > /tmp/handoff_c189.log 2>&1 &
        echo "   C188→C189 monitor: PID $! (log: /tmp/handoff_c189.log)"
        ;;
    *)
        echo "❌ Invalid start point: $START_FROM"
        echo "   Valid options: C186 (auto-detect), C187, C188, C189"
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "CAMPAIGN AUTOMATION ACTIVE"
echo "================================================================================"
echo ""
echo "The validation campaign will now run automatically with zero manual intervention."
echo ""
echo "Monitor progress:"
echo "  tail -f /tmp/c186_output.log  # C186 experiment"
echo "  tail -f /tmp/c187_output.log  # C187 experiment (after C186)"
echo "  tail -f /tmp/c188_output.log  # C188 experiment (after C187)"
echo "  tail -f /tmp/c189_output.log  # C189 experiment (after C188)"
echo "  tail -f /tmp/handoff_*.log    # Handoff monitors"
echo ""
echo "Campaign will complete in ~28 hours with 180 experiments."
echo ""
