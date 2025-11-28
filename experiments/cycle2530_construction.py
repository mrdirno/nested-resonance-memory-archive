"""
Cycle 2530: The Construction (Gate 158)
Experiment: Physical Modification.
Goal: Verify agents can build permanent structures.
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

def run_construction_experiment():
    print("🏗️ CYCLE 2530: THE CONSTRUCTION - FORTIFICATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 500
    
    # Seed Builders
    print("👷 Seeding The Masons...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Mason-{i}", lineage_id="Builders")
        agent.energy = 500
        agent.x = 50 + random.randint(-5, 5)
        agent.y = 50 + random.randint(-5, 5)
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2530_construction.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "walls_built"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Inject Predator Signal to trigger defense
            # We don't spawn a real predator, just the fear of one.
            for agent in env.agents:
                agent.sensed_signals['PREDATOR'] = (agent.x + 10, agent.y + 10)
            
            env.update()
            
            walls = len([s for s in env.structures if s['type'] == 'WALL'])
            
            writer.writerow([tick, len(env.agents), walls])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Walls={walls}")
            
            if walls >= 10:
                print("🏰 SUCCESS! The Masons have built a fortress.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_construction_experiment()
