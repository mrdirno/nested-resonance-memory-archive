"""
Cycle 2513: The Nuclear Deterrent (Gate 141)
Experiment: Mutually Assured Destruction (MAD).
Goal: Stabilize peace via threat of annihilation.
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

def run_deterrence_experiment():
    print("☢️ CYCLE 2513: THE NUCLEAR DETERRENT - MAD")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Factions
    # Republic (Weak but Smart & Rich) -> Nuclear Capable
    print("🔵 Seeding The Republic (Nuclear Capable)...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Rep-{i}", lineage_id="Republic")
        agent.energy = 1500 # Enough to build nuke
        # [..., Hunting=0.2, Altruism=0.9, ..., Trust=0.9, Innovation=0.9]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.2, 0.9, 0.5, 0.1, 0.9, 0.9]
        env.add_agent(agent)
        
    # Empire (Strong but Dumb) -> Non-Nuclear
    print("🔴 Seeding The Empire (Non-Nuclear)...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Emp-{i}", lineage_id="Empire")
        agent.energy = 500 # Not enough for nuke
        # [..., Hunting=0.9, Altruism=0.1, ..., Trust=0.1, Innovation=0.1]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.9, 0.1, 0.5, 0.1, 0.1, 0.1]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2513_deterrence.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_republic", "pop_empire", "nukes_built", "battles"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            battles = 0
            
            # Force update acts to build nukes
            for agent in env.agents:
                agent.act()
            
            republic = [a for a in env.agents if a.lineage_id == "Republic"]
            empire = [a for a in env.agents if a.lineage_id == "Empire"]
            nukes = len([a for a in republic if a.has_nuke])
            
            random.shuffle(empire)
            random.shuffle(republic)
            
            # Empire attempts to attack
            for attacker in empire:
                if not republic: break
                if attacker.energy > 50:
                    target = random.choice(republic)
                    
                    # Check if attack happens (Deterrence logic is inside attack())
                    # We need to detect if attack was aborted.
                    # attack() returns None.
                    # Let's check energy change or just assume logic works.
                    
                    prev_energy = target.energy
                    attacker.attack(target)
                    
                    if target.energy < prev_energy:
                        battles += 1
                        
            # Republic retaliation? Only if attacked.
            # But Republic is passive in this scenario (Deterrence test).
            
            env.update()
            
            writer.writerow([tick, len(republic), len(empire), nukes, battles])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Rep={len(republic)}, Emp={len(empire)}, Nukes={nukes}, Battles={battles}")
            
            if len(republic) == 0:
                print("💀 REPUBLIC ANNIHILATED.")
                break
            if len(empire) == 0:
                print("💀 EMPIRE ANNIHILATED.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Rep={len(republic)} (Nukes={nukes}), Emp={len(empire)}")

if __name__ == "__main__":
    run_deterrence_experiment()
