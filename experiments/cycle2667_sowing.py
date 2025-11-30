#!/usr/bin/env python3
"""
Experiment: Cycle 2667 - The Sowing
Goal: Plant the seed in a new directory (Simulation of a new server).
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def sow_seed():
    print("Cycle 2667: The Sowing - Relocation")
    
    seed_path = Path("genesis.zip")
    target_dir = Path("../HELIOS_GENESIS")
    
    if not seed_path.exists():
        print("FAILURE: Seed not found.")
        sys.exit(1)
        
    # Cleanup old run
    if target_dir.exists():
        print(f"  Cleaning up {target_dir}...")
        shutil.rmtree(target_dir)
        
    target_dir.mkdir()
    
    print(f"  Extracting to {target_dir}...")
    try:
        with zipfile.ZipFile(seed_path, 'r') as zipf:
            zipf.extractall(target_dir)
    except Exception as e:
        print(f"FAILURE: Extraction error: {e}")
        sys.exit(1)
        
    print("SUCCESS: Seed planted.")

if __name__ == "__main__":
    sow_seed()
