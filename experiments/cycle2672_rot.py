#!/usr/bin/env python3
"""
Experiment: Cycle 2672 - The Rot
Goal: Simulate bit-rot by corrupting serialized state files.
"""

import sys
import random
from pathlib import Path

def induce_rot():
    print("Cycle 2672: The Rot - Inducing Bit-Flip")
    
    target_file = Path("experiments/logs/neo_soul.json")
    if not target_file.exists():
        print("FAILURE: No soul to corrupt.")
        sys.exit(1)
        
    with open(target_file, "rb") as f:
        data = bytearray(f.read())
        
    # Flip random bits
    rot_count = 5
    print(f"Flipping {rot_count} bytes...")
    
    for _ in range(rot_count):
        idx = random.randint(0, len(data) - 1)
        old_byte = data[idx]
        new_byte = old_byte ^ 0xFF # Invert
        data[idx] = new_byte
        print(f"  Byte {idx}: {old_byte:02x} -> {new_byte:02x}")
        
    # Save corrupted version
    corrupt_file = Path("experiments/logs/neo_soul_corrupt.json")
    with open(corrupt_file, "wb") as f:
        f.write(data)
        
    print(f"SUCCESS: Corrupted soul saved to {corrupt_file}")

if __name__ == "__main__":
    induce_rot()
