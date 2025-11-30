#!/usr/bin/env python3
"""
Experiment: Cycle 2666 - The Seed (Robust)
Goal: Compress the project, handling missing files gracefully.
"""

import os
import zipfile
from pathlib import Path

def create_seed():
    print("Cycle 2666: The Seed - Compressing Reality")
    
    source_dir = Path(".")
    output_filename = "genesis.zip"
    
    # Excludes
    excludes = {
        '__pycache__', '.git', '.venv', 'venv', 'node_modules', 
        'genesis.zip', 'experiments/logs', '.gemini'
    }
    
    file_count = 0
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Filter dirs in-place
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                if file in excludes or file.endswith('.zip'): continue
                
                file_path = Path(root) / file
                
                # Safety check
                if not file_path.exists():
                    print(f"  [WARN] Skipping missing file: {file_path}")
                    continue
                    
                arcname = file_path.relative_to(source_dir)
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                except Exception as e:
                    print(f"  [ERR] Failed to pack {file_path}: {e}")
                    
    print(f"SUCCESS: Genesis seed created at {output_filename}")
    print(f"Files Packed: {file_count}")
    print(f"Size: {os.path.getsize(output_filename)} bytes")

if __name__ == "__main__":
    create_seed()
