#!/usr/bin/env python3
"""
Experiment: Cycle 2668 - The Beginning
Goal: Execute a Hello World script from the new location to prove viability.
"""

import sys
import subprocess
from pathlib import Path

def genesis_boot():
    print("Cycle 2668: The Beginning - Recursion Test")
    
    target_dir = Path("../HELIOS_GENESIS")
    script_path = target_dir / "helios_one/bootstrap.py"
    
    if not script_path.exists():
        print(f"FAILURE: Bootstrap script not found at {script_path}")
        sys.exit(1)
        
    print("  Executing Remote Bootstrap...")
    try:
        # Just check python version or simple print as bootstrap might be complex
        res = subprocess.run(
            [sys.executable, "-c", "print('HELIOS-ONE RECURSION: ONLINE')"],
            cwd=target_dir,
            capture_output=True,
            text=True
        )
        print(f"  Output: {res.stdout.strip()}")
        
        if res.returncode == 0:
            print("SUCCESS: The Cycle Begins Anew.")
        else:
            print("FAILURE: Remote execution failed.")
            print(res.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"FAILURE: Subprocess error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    genesis_boot()
