"""
Cycle 2532: The City (Gate 160)
Experiment: Proactive Investment.
Goal: Agents build Farms when resources are scarce but they have initial capital.
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

def run_city_experiment():
    print("🏙️ CYCLE 2532: THE CITY - URBANIZATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 1000
    
    # Seed Investors
    print("👨‍🌾 Seeding The Planters...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Planter-{i}", lineage_id="Builders")
        agent.energy = 800 # Very Rich
        agent.x = 50 + random.randint(-10, 10)
        agent.y = 50 + random.randint(-10, 10)
        # High Innovation required for Investment
        agent.genome = [0.5] * 11
        agent.genome[9] = 0.9 # Innovation
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2532_city.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "farms_built", "avg_energy"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # No free food injection! They must build farms or starve.
            # Initial energy 800 / 1.0 cost = 800 ticks survival.
            
            env.update()
            
            farms = len([s for s in env.structures if s['type'] == 'FARM'])
            avg_energy = sum(a.energy for a in env.agents) / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), farms, f"{avg_energy:.1f}"])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, Farms={farms}, Energy={avg_energy:.1f}")
            
            if farms >= 5:
                print("🌾 SUCCESS! The City is feeding itself.")
                break
                
            if len(env.agents) == 0:
                print("💀 FAILURE. Starvation.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_city_experiment()
