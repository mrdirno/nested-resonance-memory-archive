#!/bin/bash
# Build Script for Helios 3D Engine (macOS)

echo "=== HELIOS 3D ENGINE BUILD SYSTEM ==="

# 1. Build Native Bridge
echo "[1/3] Building Native Swift Bridge..."
cd ../helios_native_bridge
swift build -c release
CLI_PATH=$(pwd)/.build/release/HeliosCLI
cd ../helios_3d_engine

if [ ! -f "$CLI_PATH" ]; then
    echo "Error: HeliosCLI failed to build."
    exit 1
fi
echo "Bridge Built: $CLI_PATH"

# 2. Install PyInstaller (if needed)
if ! command -v pyinstaller &> /dev/null; then
    echo "[2/3] PyInstaller not found. Attempting install..."
    pip install pyinstaller
fi

# 3. Package App
echo "[3/3] Packaging Application..."
pyinstaller --noconfirm --clean helios.spec

echo "=== BUILD COMPLETE ==="
echo "App Bundle: dist/Helios3D.app"
