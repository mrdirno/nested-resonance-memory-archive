"""
Cycle 2511: The Republic (Gate 139)
Experiment: Governance and Law.
Goal: Can the Rich self-regulate via taxes and subsidies?
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
    print("🏛️ CYCLE 2511: THE REPUBLIC - GOVERNANCE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 3 Groups (Political Factions)
    
    # Group A: The Philanthropists (Rich, Altruistic) -> High Tax, High Subsidy
    for i in range(10):
        agent = DigitalLifeform(name=f"Liberal-{i}", lineage_id="Capital")
        agent.energy = 2000 
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.5] # Altruism=0.9
        env.add_agent(agent)
        
    # Group B: The Libertarians (Rich, Selfish) -> Low Tax, Low Subsidy
    for i in range(10):
        agent = DigitalLifeform(name=f"Conservative-{i}", lineage_id="Capital")
        agent.energy = 2000
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, 0.5] # Altruism=0.1
        env.add_agent(agent)
        
    # Group C: The Masses (Poor)
    for i in range(180):
        agent = DigitalLifeform(name=f"Citizen-{i}", lineage_id="Labor")
        agent.energy = 50
        # Mixed genes
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2511_governance.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "tax_rate", "subsidy", "treasury", "pop_rich", "pop_poor", "avg_nrg_poor"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            env.update()
            
            # Stats
            rich = [a for a in env.agents if a.energy > 1000]
            poor = [a for a in env.agents if a.energy < 100]
            
            avg_nrg_poor = 0
            if poor: avg_nrg_poor = sum(a.energy for a in poor) / len(poor)
            
            writer.writerow([tick, f"{env.tax_rate:.3f}", f"{env.subsidy_amount:.1f}", f"{env.treasury:.1f}", len(rich), len(poor), f"{avg_nrg_poor:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Tax={env.tax_rate:.1%}, Sub={env.subsidy_amount:.1f}, Treas={env.treasury:.0f}, Rich={len(rich)}, Poor={len(poor)}")
            
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Tax Rate: {env.tax_rate:.1%}")

if __name__ == "__main__":
    run_governance_experiment()
