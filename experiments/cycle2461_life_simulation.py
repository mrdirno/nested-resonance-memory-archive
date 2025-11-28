"""
Cycle 2461: The First Simulation (Gate 89)
Role: The Observer
Responsibility: Run a long-term simulation of the Ecosystem.

Objective:
- Run for 1000 ticks.
- Log population dynamics.
- Observe stability.
"""

import sys
import os
import csv
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_simulation():
    print("🌍 CYCLE 2461: INITIATING LIFE SIMULATION")
    
    # Setup
    capacity = 50
    duration = 1000
    env = Ecosystem(capacity=capacity)
    
    # Seed Population
    print("🌱 Seeding population...")
    for i in range(5):
        agent = DigitalLifeform(name=f"Eve-{i}")
        agent.energy = 150 # Good start
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2461_population.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_energy"])
        
        # Simulation Loop
        env.running = True
        for tick in range(1, duration + 1):
            env.update()
            
            # Collect Stats
            pop_count = len(env.agents)
            if pop_count > 0:
                avg_energy = sum(a.energy for a in env.agents) / pop_count
            else:
                avg_energy = 0
                
            writer.writerow([tick, pop_count, f"{avg_energy:.2f}"])
            
            # Console Feedback (every 100 ticks)
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={pop_count}, AvgEnergy={avg_energy:.1f}")
            
            if pop_count == 0:
                print("💀 EXTINCTION EVENT. Simulation ended early.")
                break
                
    print("✅ SIMULATION COMPLETE.")
    print(f"   Final Population: {len(env.agents)}")

if __name__ == "__main__":
    run_simulation()
