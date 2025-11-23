#!/usr/bin/env python3
"""
Convert Cycle 255 data format to Paper 3 expected format.

C255 format: {"conditions": {"OFF-OFF": {...}, ...}}
Paper 3 format: {"results": [{"condition_name": "OFF-OFF", ...}, ...]}

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import sys
from pathlib import Path

def convert_format(input_path: Path, output_path: Path):
    """Convert C255 format to Paper 3 expected format."""

    with open(input_path, 'r') as f:
        data = json.load(f)

    # Extract conditions dict
    conditions = data.get('conditions', {})

    # Convert to results list
    results = []
    for condition_name, condition_data in conditions.items():
        # Add condition_name to each condition's data
        condition_data['condition_name'] = condition_name
        results.append(condition_data)

    # Create output structure
    output = {
        'metadata': data.get('metadata', {}),
        'results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Converted {len(results)} conditions")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_cycle255_format.py <input.json> <output.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    convert_format(input_path, output_path)
