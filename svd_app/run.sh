#!/bin/bash
export PYTHONUNBUFFERED=1
echo "Setting up SVD-XT Standalone UI..."

# Check if python3 exists
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found."
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo "Starting the UI..."
python app.py