#!/usr/bin/env python3
"""
CYCLE 1943: TRANSCENDENTAL SHAPING

Testing the hypothesis that fundamental constants (Pi, Phi, Sqrt2) can drive
complex acoustic shaping functions (Rings, Lines, Spirals).

We use the new 'TranscendentalShapes' library to generate phase maps for the
HELIOS Universal Operator and visualize the resulting pressure fields.
"""
import sys
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')

from nrm_core.helios.operator import UniversalOperator
from bridge.transcendental_bridge import TranscendentalShapes

def print_field_slice(field_data, title):
    """
    Prints a low-res ASCII heatmap of the field slice.
    """
    print(f"\n--- {title} ---")
    rows = len(field_data)
    cols = len(field_data[0])
    
    # Downsample for ASCII (e.g., 50x50 -> 25x25)
    step = 2
    chars = " .:-=+*#%@"
    
    for y in range(0, rows, step):
        line = ""
        for x in range(0, cols, step):
            # Average local block
            val = field_data[y][x]
            # Normalize roughly (assuming max intensity ~4-16 for constructive interference)
            norm_val = min(val / 8.0, 1.0) 
            char_idx = int(norm_val * (len(chars) - 1))
            line += chars[char_idx]
        print(line)

def main():
    print("Initializing HELIOS Universal Operator...")
    # CPU mode for safety/compatibility in this context
    op = UniversalOperator(resolution_mm=2.0, use_gpu=False)
    
    # 1. Bessel Ring (Mound/Corral)
    print("\nGenerating BESSEL RING (Scale=0.5)...")
    func_ring = TranscendentalShapes.bessel_ring(scale=0.5)
    op.apply_phase_function(func_ring)
    ring_slice = op.get_field_slice(z_ratio=0.5)
    print_field_slice(ring_slice, "BESSEL RING FIELD")
    
    # 2. Diagonal Line (Root 2)
    print("\nGenerating DIAGONAL LINE (Root 2)...")
    func_line = TranscendentalShapes.diagonal_line(period=20.0)
    op.apply_phase_function(func_line)
    line_slice = op.get_field_slice(z_ratio=0.5)
    print_field_slice(line_slice, "DIAGONAL LINE FIELD")
    
    # 3. Golden Spiral (Phi)
    print("\nGenerating GOLDEN SPIRAL (Phi)...")
    func_spiral = TranscendentalShapes.golden_spiral(twist=2.0)
    op.apply_phase_function(func_spiral)
    spiral_slice = op.get_field_slice(z_ratio=0.5)
    print_field_slice(spiral_slice, "GOLDEN SPIRAL FIELD")

    print("\nTranscendental Shaping Test Complete.")

if __name__ == "__main__":
    main()
