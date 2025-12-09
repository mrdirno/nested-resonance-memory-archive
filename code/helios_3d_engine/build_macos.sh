#!/bin/bash
# Build Script for Helios 3D Engine (macOS)

echo "=== HELIOS 3D ENGINE BUILD SYSTEM ==="

# 1. Install PyInstaller (if needed)
if ! command -v pyinstaller &> /dev/null; then
    echo "[1/2] PyInstaller not found. Attempting install..."
    pip install pyinstaller
else
    echo "[1/2] PyInstaller found."
fi

# 2. Package App
echo "[2/2] Packaging Application..."
pyinstaller --noconfirm --clean helios.spec

echo "=== BUILD COMPLETE ==="
echo "App Bundle: dist/Helios3D.app"
