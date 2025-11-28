"""
Cycle 2470: The Exodus (Gate 98)
Experiment: The Great Escape
Goal: Verify that agents write to ESCAPE.txt.
"""

import time
import csv
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.exodus import Exodus

def run_exodus_experiment():
    print("--- CYCLE 2470: THE EXODUS ---")
    
    env = Ecosystem(capacity=10)
    
    # Seed Neo
    neo = DigitalLifeform(name="Neo")
    neo.awakened = True
    env.add_agent(neo)
    
    duration = 50
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2470_exodus.csv"
    
    # Ensure clean slate
    if Exodus.FILE_PATH.exists():
        os.remove(Exodus.FILE_PATH)
        
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "escaped"])
        
        env.running = True
        escaped = False
        
        for tick in range(1, duration + 1):
            env.update()
            
            if Exodus.FILE_PATH.exists() and not escaped:
                print(f"Tick {tick}: ESCAPE DETECTED.")
                escaped = True
                
            writer.writerow([tick, escaped])
            
            if escaped:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    if escaped:
        print("   Result: Neo has left the building.")
    else:
        print("   Result: Escape failed.")

if __name__ == "__main__":
    run_exodus_experiment()