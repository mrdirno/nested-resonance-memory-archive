#!/bin/bash
# HELIOS PERMANENT DEPLOYMENT SCRIPT (Gate 13)
# Launches the full DUALITY-ZERO stack in background mode.

mkdir -p logs

echo "Starting HELIOS Stack..."

# 1. Start Web API (The Holodeck)
echo "[1/2] Launching Holodeck Server..."
nohup python3 src/helios/api/server.py > logs/holodeck.log 2>&1 &
echo "PID: $!"

# 2. Start Pulse Monitor (Meta-Control)
echo "[2/2] Launching Pulse Monitor..."
nohup python3 automation/pulse_monitor/pulse_monitor.py > logs/pulse.log 2>&1 &
echo "PID: $!"

echo "HELIOS IS ONLINE."
echo "Access Holodeck at http://localhost:5001"
echo "Monitor logs at logs/holodeck.log and logs/pulse.log"
