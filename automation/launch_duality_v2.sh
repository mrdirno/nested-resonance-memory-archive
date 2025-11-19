#!/bin/bash
# DUALITY-ZERO-V2 Automation Launcher
# Hybrid Reality-Fractal Intelligence System

echo "═══════════════════════════════════════════════════════════════"
echo "            DUALITY-ZERO-V2 AUTOMATION SYSTEM                 "
echo "           Hybrid Reality-Fractal Intelligence                "
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
DUALITY_V2_ROOT="/Volumes/dual/DUALITY-ZERO-V2"
AUTOMATION_SCRIPT="/Users/aldrinpayopay/Desktop/DUALITY-ZERO/USER-PROTECTED-DO-NOT-DELETE/claude_code_automation_macos.py"
CLAUDE_FLAGS="--dangerously-skip-permissions"

# Check if external drive is mounted
if [ ! -d "$DUALITY_V2_ROOT" ]; then
    echo "❌ ERROR: DUALITY-ZERO-V2 not found at $DUALITY_V2_ROOT"
    echo "Please ensure the external SSD is mounted."
    exit 1
fi

# Function to launch Claude with proper flags
launch_claude() {
    echo "🚀 Launching Claude CLI with permissionless mode..."
    cd "$DUALITY_V2_ROOT"
    claude $CLAUDE_FLAGS
}

# Function to launch automation tool
launch_automation() {
    echo "🤖 Launching DUALITY-ZERO-V2 Automation Tool..."
    if [ -f "$AUTOMATION_SCRIPT" ]; then
        python3 "$AUTOMATION_SCRIPT"
    else
        echo "❌ Automation script not found at: $AUTOMATION_SCRIPT"
        echo "Creating link to V2 automation..."
        # Create new automation script if needed
        cp "$AUTOMATION_SCRIPT" "$DUALITY_V2_ROOT/automation/duality_v2_automation.py" 2>/dev/null
    fi
}

# Menu
echo "Select operation mode:"
echo "1) Launch Claude CLI (permissionless mode)"
echo "2) Launch Automation Tool (GUI)"
echo "3) Launch Meta-Orchestration (Start Autonomous Cycles) ⭐"
echo "4) Launch Claude + Automation"
echo "5) Update System"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        launch_claude
        ;;
    2)
        launch_automation
        ;;
    3)
        # Launch Meta-Orchestration - Create 2 Claude windows and start automation
        echo "🎯 Starting DUALITY-ZERO-V2 Meta-Orchestration..."
        echo "This will:"
        echo "  - Launch automation GUI"
        echo "  - You'll need to: Create 2 Claude windows, record click locations, start automation"
        echo ""
        echo "Press Enter to continue..."
        read
        launch_automation
        ;;
    4)
        # Launch Claude in background
        echo "Launching Claude in new terminal window..."
        osascript -e "tell application \"Terminal\" to do script \"cd $DUALITY_V2_ROOT && claude $CLAUDE_FLAGS\""
        sleep 2
        launch_automation
        ;;
    5)
        echo "🔄 Updating DUALITY-ZERO-V2..."
        cd "$DUALITY_V2_ROOT"
        git pull 2>/dev/null || echo "Not a git repository yet"
        echo "✅ Update complete"
        ;;
    6)
        echo "👋 Exiting DUALITY-ZERO-V2"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac