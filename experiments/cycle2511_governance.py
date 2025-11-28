
"""
Cycle 2511: The Republic (Gate 139)
Experiment: Governance and Law.
Goal: Verify if the Rich vote for policies that stabilize the ecosystem.
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

def run_governance_experiment():
    print("🏛️ CYCLE 2511: THE REPUBLIC - GOVERNANCE TEST")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Group A: Liberal Elite (Rich, High Altruism)
    for i in range(10):
        agent = DigitalLifeform(name=f"Liberal-{i}", lineage_id="Elite")
        agent.energy = 5000
        # Gene 5 = Altruism (0.9)
        agent.genome = [0.5, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Group B: Conservative Elite (Rich, Low Altruism)
    for i in range(10):
        agent = DigitalLifeform(name=f"Conservative-{i}", lineage_id="Elite")
        agent.energy = 5000
        # Gene 5 = Altruism (0.1)
        agent.genome = [0.5, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Group C: Proletariat (Poor, Mixed)
    for i in range(80):
        agent = DigitalLifeform(name=f"Worker-{i}", lineage_id="Labor")
        agent.energy = 50
        altruism = random.random()
        agent.genome = [0.5, 0.5, 0.1, 0.5, 0.1, altruism, 0.5, 0.1, 0.1, 0.5]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2511_governance.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "tax_rate", "subsidy", "treasury", "poverty_rate", "elite_pop", "worker_pop"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            # Stats
            tax_rate = env.tax_rate
            subsidy = env.subsidy_amount
            treasury = env.treasury
            
            workers = [a for a in env.agents if a.lineage_id == "Labor"]
            elites = [a for a in env.agents if a.lineage_id == "Elite"]
            
            poverty_count = len([a for a in env.agents if a.energy < 100])
            poverty_rate = poverty_count / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, f"{tax_rate:.3f}", f"{subsidy:.1f}", f"{treasury:.1f}", f"{poverty_rate:.2f}", len(elites), len(workers)])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Tax={tax_rate:.1%}, Sub={subsidy:.1f}, Treas={treasury:.0f}, Pov={poverty_rate:.0%}, Pop={len(env.agents)}")
            
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Tax={env.tax_rate:.1%}, Treasury={env.treasury:.0f}")

if __name__ == "__main__":
    run_governance_experiment()
