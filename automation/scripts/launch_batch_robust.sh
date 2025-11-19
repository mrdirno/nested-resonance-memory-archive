#!/bin/bash
# Robust launch script for C256-C260 batch

echo "Launching C256 (H1xH4)..."
nohup python3 -u experiments/cycle256_h1h4_optimized.py > experiments/logs/cycle256_execution.log 2>&1 &
echo "PID $!"

echo "Launching C257 (H1xH5)..."
nohup python3 -u experiments/cycle257_h1h5_optimized.py > experiments/logs/cycle257_execution.log 2>&1 &
echo "PID $!"

echo "Launching C258 (H2xH4)..."
nohup python3 -u experiments/cycle258_h2h4_optimized.py > experiments/logs/cycle258_execution.log 2>&1 &
echo "PID $!"

echo "Launching C259 (H2xH5)..."
nohup python3 -u experiments/cycle259_h2h5_optimized.py > experiments/logs/cycle259_execution.log 2>&1 &
echo "PID $!"

echo "Launching C260 (H4xH5)..."
nohup python3 -u experiments/cycle260_h4h5_optimized.py > experiments/logs/cycle260_execution.log 2>&1 &
echo "PID $!"

echo "All experiments launched."
