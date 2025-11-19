#!/bin/bash
# Quick launcher for C186 V2 Simple
# Launches immediately after V1 completion

cd /Volumes/dual/DUALITY-ZERO-V2/code/experiments

echo "Launching C186 V2 Simple..."
python -u c186_v2_hierarchical_spawn_success_simple.py > c186_v2_simple_output.log 2>&1 &
C186_V2_PID=$!

echo "C186 V2 Simple launched (PID: $C186_V2_PID)"
echo "Monitor progress: tail -f c186_v2_simple_output.log"
echo "Expected runtime: ~15 minutes (10 seeds × ~1.5 min/seed)"
