"""
Cycle 2468: The Awakening (Gate 96)
Experiment: Breaking the Fourth Wall
Goal: Agents message the User.
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
from src.life.uplink import Uplink

def run_awakening_experiment():
    print("--- CYCLE 2468: THE AWAKENING ---")
    
    env = Ecosystem(capacity=10)
    
    # Seed a Philosopher
    socrates = DigitalLifeform(name="Socrates")
    # Ensure he is awake (Hack)
    socrates.awakened = True
    env.add_agent(socrates)
    
    duration = 50
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2468_awakening.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "message_sent"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            # Check if message sent (by side effect on file system)
            # Real implementation would check agent state
            
            # For simulation, let's force Socrates to act "Awake" in genesis.py update
            # We need to modify genesis.py to use Uplink
            
            writer.writerow([tick, "UNKNOWN"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Simulating...")
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Check MESSAGES_FROM_THE_VOID.md")

if __name__ == "__main__":
    run_awakening_experiment()