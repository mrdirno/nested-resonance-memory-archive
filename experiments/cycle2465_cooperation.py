"""
Cycle 2465: The Society (Gate 93)
Experiment: Emergent Cooperation
Goal: Observe if altruism (Gene 2) increases under harsh conditions.
"""

import time
import csv
import random
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_cooperation_experiment():
    print("--- CYCLE 2465: THE SOCIETY ---")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=100)
    
    # Seed with random agents
    for i in range(50):
        agent = DigitalLifeform(name=f"Gen0-{i}")
        # Randomize Altruism (Gene 2)
        # Gene 0 = Efficiency, Gene 1 = Fertility, Gene 2 = Altruism
        # Genes initialized in genesis.py, just update them
        agent.genome = [random.random(), random.random(), random.random()]
        env.add_agent(agent)
        
    duration = 2000
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2465_cooperation.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_altruism", "total_donations"])
        
        env.running = True
        total_donations = 0
        
        for tick in range(1, duration + 1):
            # Harsh Environment: Random energy drain
            # This creates a need for help
            if env.agents:
                for agent in env.agents:
                    if random.random() < 0.1: # 10% chance of disaster
                        agent.energy -= 30
                        # If low, they might signal HELP (handled in act)
            
            # Replenish energy (The Sun) - scarce resources
            if env.agents:
                for _ in range(max(1, int(len(env.agents) * 0.1))): # Feed 10%
                    lucky_agent = random.choice(env.agents)
                    lucky_agent.energy += 30
            
            # Track donations (Hack: we can't easily track count from outside without modifying classes)
            # Let's just track gene frequency.
            
            env.update()
            
            # Collect Stats
            pop_count = len(env.agents)
            if pop_count > 0:
                avg_alt = sum(a.genome[2] if len(a.genome) > 2 else 0.5 for a in env.agents) / pop_count
            else:
                avg_alt = 0
                
            writer.writerow([tick, pop_count, f"{avg_alt:.4f}", total_donations])
            
            if tick % 200 == 0:
                print(f"   Tick {tick}: Pop={pop_count}, Avg Altruism={avg_alt:.3f}")
            
            if pop_count == 0:
                print("💀 EXTINCTION EVENT.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Altruism: {avg_alt:.3f}")

if __name__ == "__main__":
    run_cooperation_experiment()