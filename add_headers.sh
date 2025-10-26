#!/bin/bash
# Add attribution headers to all Python files

HEADER='"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

'

find code -name "*.py" -type f | while read file; do
    # Check if file already has the header
    if ! grep -q "Aldrin Payopay" "$file"; then
        temp_file="${file}.tmp"
        echo "$HEADER" > "$temp_file"
        cat "$file" >> "$temp_file"
        mv "$temp_file" "$file"
        echo "Added header to: $file"
    fi
done

find tests -name "*.py" -type f | while read file; do
    if ! grep -q "Aldrin Payopay" "$file"; then
        temp_file="${file}.tmp"
        echo "$HEADER" > "$temp_file"
        cat "$file" >> "$temp_file"
        mv "$temp_file" "$file"
        echo "Added header to: $file"
    fi
done
