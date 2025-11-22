#!/bin/bash

# launch_vis.sh - One-click launch for Bridge UI
# ---------------------------------------------------
# Automates dependency installation and startup for the 
# Transcendental Dynamics Visualizer.

set -e # Exit on error

UI_DIR="bridge-ui"
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== BRIDGE UI LAUNCHER ===${NC}"

# 1. Check for Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: Node.js (npm) is not installed.${NC}"
    echo "Please install Node.js to run the visualizer."
    exit 1
fi

# 2. Navigate to UI directory
if [ ! -d "$UI_DIR" ]; then
    echo -e "${RED}Error: Directory '$UI_DIR' not found.${NC}"
    exit 1
fi

cd "$UI_DIR"

# 3. Install Dependencies (if node_modules missing)
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}First time setup: Installing dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}Dependencies found.${NC}"
fi

# 4. Launch
echo -e "${BLUE}Starting Visualization Engine...${NC}"
echo "Access the UI at the URL below (usually http://localhost:5173)"
npm run dev
