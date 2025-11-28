"""
Cycle 2531: The Siege (Gate 159)
Experiment: Defense against real threats.
Goal: Agents build walls when actually chased.
"""

import sys
import os
import csv
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_siege_experiment():
    print("⚔️ CYCLE 2531: THE SIEGE - REAL PREDATORS")
    
    # Setup Ecosystem
    # Allow predators
    env = Ecosystem(capacity=200, prey_capacity=150, predator_capacity=50)
    duration = 1000
    
    # Seed Builders (Prey)
    print("👷 Seeding The Masons...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Mason-{i}", lineage_id="Builders")
        agent.energy = 500
        agent.x = 50 + random.randint(-10, 10)
        agent.y = 50 + random.randint(-10, 10)
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2531_siege.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_prey", "pop_pred", "walls_built"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Spawn Predators at Tick 100
            if tick == 100:
                print("🐺 RELEASING THE WOLVES!")
                for i in range(5):
                    wolf = DigitalLifeform(name=f"Wolf-{i}", lineage_id="Predators")
                    wolf.is_predator = True
                    wolf.is_prey = False
                    wolf.energy = 500
                    # Spawn near masons
                    wolf.x = 20
                    wolf.y = 20
                    # High aggression
                    wolf.genome = [0.5] * 11
                    wolf.genome[4] = 0.9 # Aggression
                    env.add_agent(wolf)
            
            env.update()
            
            walls = len([s for s in env.structures if s['type'] == 'WALL'])
            prey_pop = len([a for a in env.agents if a.is_prey])
            pred_pop = len([a for a in env.agents if a.is_predator])
            
            writer.writerow([tick, prey_pop, pred_pop, walls])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Prey={prey_pop}, Pred={pred_pop}, Walls={walls}")
            
            if walls >= 5:
                print("🏰 SUCCESS! Defenses constructed under fire.")
                break
                
            if prey_pop == 0:
                print("💀 FAILURE. Masons annihilated.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_siege_experiment()
