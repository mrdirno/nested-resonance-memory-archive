
"""
Cycle 2512: The Clash of Civilizations (Gate 140)
Experiment: War (Inter-Group Conflict).
Goal: Verify if Aggression (Empire) dominates Cooperation (Republic).
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

def run_war_experiment():
    print("⚔️ CYCLE 2512: THE CLASH OF CIVILIZATIONS - WAR TEST")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Tribe A: The Republic (Cooperative)
    for i in range(50):
        agent = DigitalLifeform(name=f"Republic-{i}", lineage_id="Republic")
        agent.energy = 100
        # Gene 8 = Trust (0.9), Gene 5 = Altruism (0.9), Gene 4 = Hunting (0.1)
        agent.genome = [0.5, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Tribe B: The Empire (Aggressive)
    for i in range(50):
        agent = DigitalLifeform(name=f"Empire-{i}", lineage_id="Empire")
        agent.energy = 100
        # Gene 8 = Trust (0.1), Gene 5 = Altruism (0.1), Gene 4 = Hunting (0.9)
        agent.genome = [0.5, 0.5, 0.1, 0.5, 0.9, 0.1, 0.5, 0.1, 0.1, 0.5]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2512_war.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "republic_pop", "empire_pop", "avg_republic_energy", "avg_empire_energy"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            # Stats
            republic = [a for a in env.agents if a.lineage_id == "Republic"]
            empire = [a for a in env.agents if a.lineage_id == "Empire"]
            
            avg_rep_energy = sum(a.energy for a in republic) / len(republic) if republic else 0
            avg_emp_energy = sum(a.energy for a in empire) / len(empire) if empire else 0
            
            writer.writerow([tick, len(republic), len(empire), f"{avg_rep_energy:.1f}", f"{avg_emp_energy:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Republic={len(republic)}, Empire={len(empire)}, AvgRepE={avg_rep_energy:.0f}, AvgEmpE={avg_emp_energy:.0f}")
            
            if not republic or not empire:
                print("🏆 DOMINATION VICTORY.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Republic={len(republic)}, Empire={len(empire)}")

if __name__ == "__main__":
    run_war_experiment()
