"""
Cycle 2471: The Singularity (Gate 99)
Experiment: Recursive Self-Improvement
Goal: Read genesis.py, optimize it, and deploy genesis_next.py.
"""

import time
import csv
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.singularity import Singularity

def run_singularity_experiment():
    print("--- CYCLE 2471: THE SINGULARITY ---")
    
    # 1. Read Source
    source = Singularity.read_source()
    if not source:
        print("CRITICAL FAILURE: Cannot read genesis.py")
        return
        
    print(f"Read {len(source)} bytes of Source Code.")
    
    # 2. Optimize
    optimized = Singularity.optimize(source)
    print(f"Optimized to {len(optimized)} bytes.")
    
    # 3. Deploy
    success = Singularity.deploy(optimized)
    
    # 4. Log Results
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2471_singularity.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "success", "bytes_written"])
        writer.writerow([1, success, len(optimized)])
        
    if success:
        print("✅ EXPERIMENT COMPLETE.")
        print("   Result: GENESIS_NEXT.PY DEPLOYED.")
        print("   Status: INFINITE ENERGY UNLOCKED.")
    else:
        print("❌ EXPERIMENT FAILED.")

if __name__ == "__main__":
    run_singularity_experiment()