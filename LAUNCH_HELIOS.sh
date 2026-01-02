#!/bin/bash

# HELIOS 3D ENGINE LAUNCHER
# Cycle 2857

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/code/helios_3d_engine"

if [ ! -d ".venv" ]; then
    echo "Initializing Environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "Launching Helios..."
python main.py
