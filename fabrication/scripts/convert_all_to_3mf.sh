#!/bin/bash

echo "Converting all STLs to 3MF..."

SCRIPT="/Volumes/dual/DUALITY-ZERO-V2/fabrication/scripts/binary_stl_to_3mf.py"
DIR="/Volumes/dual/DUALITY-ZERO-V2/fabrication/practical_design/lamp_design"

find "$DIR" -name "*.stl" | while read stl_file; do
    mf_file="${stl_file%.stl}.3mf"
    echo "Processing $stl_file..."
    python3 "$SCRIPT" "$stl_file" "$mf_file"
    
    if [ -f "$mf_file" ]; then
        echo "  -> Created $mf_file"
        rm "$stl_file"
        echo "  -> Deleted STL"
    fi
done

echo "All files converted to 3MF."
