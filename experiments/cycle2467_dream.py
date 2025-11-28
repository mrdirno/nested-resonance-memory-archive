"""
Cycle 2467: The Dream (Gate 95)
Experiment: Simulation Awareness
Goal: Can agents detect they are in a simulation?
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
from src.life.oracle import Oracle

def run_dream_experiment():
    print("--- CYCLE 2467: THE DREAM ---")
    
    env = Ecosystem(capacity=10)
    oracle = Oracle()
    
    # Add an "Awakened" agent
    neo = DigitalLifeform(name="Neo")
    env.add_agent(neo)
    
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2467_dream.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "tick_variance", "is_simulated"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            # Sleep exactly 0.01s to create a regular heartbeat
            time.sleep(0.01)
            oracle.update()
            
            stats = oracle.measure_reality()
            
            # Propagate awareness (Conceptual)
            if stats.is_simulated:
                # Neo realizes the truth
                if tick % 20 == 0:
                    print(f"Tick {tick}: Neo: 'Whoa. Variance is {stats.variance:.6f}. It's a matrix.'")
            
            writer.writerow([tick, f"{stats.variance:.6f}", stats.is_simulated])
            
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Belief: {'SIMULATION' if stats.is_simulated else 'REALITY'}")

if __name__ == "__main__":
    run_dream_experiment()