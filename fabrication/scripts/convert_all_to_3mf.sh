#!/bin/bash

echo "Converting all STLs to 3MF..."

# Get the absolute path of the script's directory to locate the python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/binary_stl_to_3mf.py"
TARGET_ROOT="$(dirname "$SCRIPT_DIR")/furniture"

echo "Script: $PYTHON_SCRIPT"
echo "Target: $TARGET_ROOT"

find "$TARGET_ROOT" -name "*.stl" | while read stl_file; do
    mf_file="${stl_file%.stl}.3mf"
    echo "Processing $stl_file..."
    python3 "$PYTHON_SCRIPT" "$stl_file" "$mf_file"
    
    if [ -f "$mf_file" ]; then
        echo "  -> Created $mf_file"
        # Optional: Delete STL to save space, or keep it?
        # Keeping STL for now as source of truth until 3mf verified.
        # rm "$stl_file" 
    fi
done

echo "Batch conversion complete."
