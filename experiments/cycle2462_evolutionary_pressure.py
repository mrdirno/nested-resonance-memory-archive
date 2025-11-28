"""
Cycle 2462: The Evolution (Gate 90)
Role: The Evolutionary Biologist
Responsibility: Observe Natural Selection.

Objective:
- Run for 2000 ticks.
- Track Efficiency (Gene 0) and Fertility (Gene 1).
- Expect directional selection (increase in both).
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

def run_evolution():
    print("🧬 CYCLE 2462: INITIATING EVOLUTIONARY PRESSURE")
    
    # Setup
    capacity = 100
    duration = 2000
    env = Ecosystem(capacity=capacity)
    
    # Seed Population with random traits (avg 0.5)
    print("🌱 Seeding population with random genomes...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Eve-{i}")
        agent.energy = 100
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2462_evolution.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_efficiency", "avg_fertility"])
        
        # Simulation Loop
        env.running = True
        for tick in range(1, duration + 1):
            # Replenish energy (The Sun)
            # Give random energy to random agents to simulate foraging
            if env.agents:
                # Feed 20% of population
                for _ in range(max(1, int(len(env.agents) * 0.2))):
                    import random
                    lucky_agent = random.choice(env.agents)
                    lucky_agent.energy += 10
            
            env.update()
            
            # Collect Stats
            pop_count = len(env.agents)
            if pop_count > 0:
                avg_eff = sum(a.genome[0] for a in env.agents) / pop_count
                avg_fert = sum(a.genome[1] for a in env.agents) / pop_count
            else:
                avg_eff = 0
                avg_fert = 0
                
            writer.writerow([tick, pop_count, f"{avg_eff:.4f}", f"{avg_fert:.4f}"])
            
            # Console Feedback (every 200 ticks)
            if tick % 200 == 0:
                print(f"   Tick {tick}: Pop={pop_count}, Eff={avg_eff:.3f}, Fert={avg_fert:.3f}")
            
            if pop_count == 0:
                print("💀 EXTINCTION EVENT. Simulation ended early.")
                break
                
    print("✅ EVOLUTION COMPLETE.")
    print(f"   Final Stats: Pop={len(env.agents)}, Eff={avg_eff:.3f}, Fert={avg_fert:.3f}")

if __name__ == "__main__":
    run_evolution()