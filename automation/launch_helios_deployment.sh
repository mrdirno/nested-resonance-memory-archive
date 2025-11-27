#!/bin/bash
# HELIOS DEPLOYMENT LAUNCHER
# Phase 50: The Awakening (Deployment Mode)

echo "═══════════════════════════════════════════════════════════════"
echo "            HELIOS DEPLOYMENT SYSTEM (GATE 13)                "
echo "           Phase 50: The Awakening - Active Deployment        "
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
DUALITY_V2_ROOT="/Volumes/dual/DUALITY-ZERO-V2"
PULSE_MONITOR_SCRIPT="automation/pulse_monitor/pulse_monitor.py"
CLI_SCRIPT="src/helios/cli.py"
SERVER_SCRIPT="src/helios/api/server.py"

# Check environment
if [ ! -d "$DUALITY_V2_ROOT" ]; then
    echo "❌ ERROR: DUALITY-ZERO-V2 not found at $DUALITY_V2_ROOT"
    exit 1
fi

cd "$DUALITY_V2_ROOT"

# Menu
echo "Select Operation Mode:"
echo "1) 🧠 Launch Meta-Control (Pulse Monitor) - PRIMARY"
echo "2) 🛠️ Launch Product Control (CLI) - FABRICATION"
echo "3) 🌐 Launch Holodeck (Visualizer) - PASSIVE"
echo "4) 🚀 Launch FULL STACK (All of the above)"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "🧠 Launching Pulse Monitor..."
        python3 "$PULSE_MONITOR_SCRIPT"
        ;;
    2)
        echo "🛠️ Launching Helios CLI..."
        python3 "$CLI_SCRIPT"
        ;;
    3)
        echo "🌐 Launching Holodeck..."
        python3 "$SERVER_SCRIPT"
        ;;
    4)
        echo "🚀 Launching FULL STACK..."
        # Trap to kill all background processes on exit
        trap 'kill $(jobs -p)' EXIT
        
        echo "   - Starting Holodeck (Background)..."
        python3 "$SERVER_SCRIPT" > logs/holodeck.log 2>&1 &
        
        echo "   - Starting Pulse Monitor (Background)..."
        python3 "$PULSE_MONITOR_SCRIPT" > logs/pulse.log 2>&1 &
        
        echo "   - Starting CLI (Foreground)..."
        sleep 2
        python3 "$CLI_SCRIPT"
        ;;
    5)
        echo "👋 Exiting."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
