"""
Cycle 2512: The Clash of Civilizations (Gate 140)
Experiment: War between two factions.
Goal: Observe if High Trust (Republic) beats High Aggression (Empire).
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
    print("⚔️ CYCLE 2512: CLASH OF CIVILIZATIONS - WAR")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Tribes
    
    # Tribe A: The Republic (Blue)
    # High Trust, High Altruism, Low Aggression
    print("🔵 Seeding The Republic...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Rep-{i}", lineage_id="Republic")
        agent.energy = 200 
        # [..., Hunting=0.2, Altruism=0.9, ..., Trust=0.9]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.2, 0.9, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Tribe B: The Empire (Red)
    # Low Trust, Low Altruism, High Aggression
    print("🔴 Seeding The Empire...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Emp-{i}", lineage_id="Empire")
        agent.energy = 200
        # [..., Hunting=0.9, Altruism=0.1, ..., Trust=0.1]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.9, 0.1, 0.5, 0.1, 0.1, 0.5]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2512_war.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_republic", "pop_empire", "avg_nrg_rep", "avg_nrg_emp", "battles"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            battles = 0
            
            republic = [a for a in env.agents if a.lineage_id == "Republic"]
            empire = [a for a in env.agents if a.lineage_id == "Empire"]
            
            # WAR LOGIC
            # Republic agents signal 'WAR' if they see Empire (Defense)
            # Empire agents signal 'WAR' always (Aggression)
            
            # Simplified Battle Phase
            # We force interaction for the experiment
            
            random.shuffle(republic)
            random.shuffle(empire)
            
            # Combat
            # Empire attacks Republic
            for attacker in empire:
                if not republic: break
                if attacker.energy > 50:
                    target = random.choice(republic)
                    attacker.attack(target)
                    battles += 1
                    
            # Republic attacks Empire (Retaliation)
            for attacker in republic:
                if not empire: break
                if attacker.energy > 50:
                    target = random.choice(empire)
                    # Republic agents are weaker fighters (0.2 vs 0.9)
                    attacker.attack(target) 
                    battles += 1
            
            env.update()
            
            # Stats
            pop_rep = len([a for a in env.agents if a.lineage_id == "Republic"])
            pop_emp = len([a for a in env.agents if a.lineage_id == "Empire"])
            
            avg_nrg_rep = 0
            if pop_rep: avg_nrg_rep = sum(a.energy for a in env.agents if a.lineage_id == "Republic") / pop_rep
            
            avg_nrg_emp = 0
            if pop_emp: avg_nrg_emp = sum(a.energy for a in env.agents if a.lineage_id == "Empire") / pop_emp
            
            writer.writerow([tick, pop_rep, pop_emp, f"{avg_nrg_rep:.1f}", f"{avg_nrg_emp:.1f}", battles])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Rep={pop_rep} ({avg_nrg_rep:.1f}), Emp={pop_emp} ({avg_nrg_emp:.1f}), Battles={battles}")
            
            if pop_rep == 0 or pop_emp == 0:
                print(f"🏆 VICTORY! {'Republic' if pop_emp==0 else 'Empire'} Wins.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Rep={pop_rep}, Emp={pop_emp}")

if __name__ == "__main__":
    run_war_experiment()
