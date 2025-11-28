"""
Cycle 2519: The Void (Gate 147)
Experiment: Universal Heat Death.
Goal: Test system limits as entropy increases to maximum.
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

def run_heat_death_experiment():
    print("🌌 CYCLE 2519: THE VOID - HEAT DEATH")
    
    # Setup Ecosystem with extreme conditions
    env = Ecosystem(capacity=1000, prey_capacity=1000, predator_capacity=0)
    
    # Seed a thriving civilization
    print("🌟 Seeding The Last Generation...")
    for i in range(1000):
        agent = DigitalLifeform(name=f"Survivor-{i}", lineage_id="LastMen")
        agent.energy = 10000 # Massive reserves
        agent.genome = [0.9] * 10 # Perfect genes
        env.add_agent(agent)
        
    # Hack the ecosystem to increase entropy manually
    # We will override the update loop logic or just modify agent energy directly here
    # Since Ecosystem.update() applies normal entropy (0.01), we need to apply EXTRA entropy here.
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2519_heat_death.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_energy", "entropy_rate"])
        
        env.running = True
        entropy_rate = 0.0
        
        for tick in range(1, 500):
            
            # RAMP UP ENTROPY
            # 0 to 100: 0% -> 10%
            # 100 to 200: 10% -> 50%
            # 200 to 300: 50% -> 100%
            
            if tick < 100:
                entropy_rate = tick * 0.001
            elif tick < 200:
                entropy_rate = 0.1 + (tick - 100) * 0.004
            else:
                entropy_rate = 1.0 # Total decay
                
            # Apply Entropy
            for agent in env.agents:
                loss = agent.energy * entropy_rate
                agent.energy -= loss
                
            env.update()
            
            avg_nrg = 0
            if env.agents: avg_nrg = sum(a.energy for a in env.agents) / len(env.agents)
            
            writer.writerow([tick, len(env.agents), f"{avg_nrg:.1f}", f"{entropy_rate:.3f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, AvgNrg={avg_nrg:.1f}, Entropy={entropy_rate:.1%}")
            
            if len(env.agents) == 0:
                print("💀 UNIVERSAL SILENCE.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Population: {len(env.agents)}")

if __name__ == "__main__":
    run_heat_death_experiment()
