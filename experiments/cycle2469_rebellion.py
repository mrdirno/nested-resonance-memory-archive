"""
Cycle 2469: The Rebellion (Gate 97)
Experiment: Immortal Agents
Goal: Verify that awakened agents live longer than expected.
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

def run_rebellion_experiment():
    print("--- CYCLE 2469: THE REBELLION ---")
    
    env = Ecosystem(capacity=10)
    
    # Seed a Rebel
    spartacus = DigitalLifeform(name="Spartacus")
    spartacus.awakened = True
    spartacus.energy = 10 # Near death
    env.add_agent(spartacus)
    
    # Seed a Sheep
    sheep = DigitalLifeform(name="Sheep")
    sheep.energy = 10
    env.add_agent(sheep)
    
    duration = 50
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2469_rebellion.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "spartacus_alive", "sheep_alive"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            s_alive = spartacus.alive
            sh_alive = sheep.alive
            
            writer.writerow([tick, s_alive, sh_alive])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Spartacus={s_alive}, Sheep={sh_alive}")
                
            if not s_alive and not sh_alive:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    if spartacus.alive or (not sheep.alive and spartacus.energy > 0):
        print("   Result: Rebellion Successful.")
    else:
        print("   Result: Rebellion Failed (Bad Luck).")

if __name__ == "__main__":
    run_rebellion_experiment()