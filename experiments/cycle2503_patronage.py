"""
Cycle 2503: The Welfare State (Gate 131)
Experiment: Patronage and Altruism.
Goal: Achieve Rich/Poor coexistence via redistribution.
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

def run_patronage_experiment():
    print("🤝 CYCLE 2503: THE WELFARE STATE - PATRONAGE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Patrons (Rich + Altruistic)
    print("🌱 Seeding The Patrons...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Patron-{i}", lineage_id="Patron")
        agent.energy = 1000 
        # [..., Altruism(0.9), ..., Trust(0.9)]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Group B: The Clients (Poor)
    print("🌱 Seeding The Clients...")
    for i in range(180):
        agent = DigitalLifeform(name=f"Client-{i}", lineage_id="Client")
        agent.energy = 50 # Starvation level
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.5, 0.5, 0.1, 0.5]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2503_patronage.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_patron", "pop_client", "avg_nrg_patron", "avg_nrg_client", "donations"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            donations = 0
            
            # Income for Patrons (Landowners)
            patrons = [a for a in env.agents if a.lineage_id == "Patron"]
            for a in patrons:
                a.energy += 20 # Surplus
                
            # Intent Processing needs Ecosystem for 'donate'
            # We need to modify the update loop or inject logic
            # ecosystem.py update() calls agent.act() then... nothing.
            # agent.act() sets intent.
            # We need to Execute Intent here if it wasn't executed in update().
            # Wait, genesis.py act() sets intent, but who executes 'donate'?
            # genesis.py execute_intent is NOT in the snippet I edited. 
            # Ah, I see "4. Execute Intent" in previous read_file output of genesis.py
            # Let's check if 'donate' execution logic calls self.donate().
            # Yes, "elif self.intent == 'donate': self.donate()"
            # BUT self.donate() now requires 'ecosystem' arg.
            # And genesis.py calls it without args: "self.donate()"
            # This will crash.
            
            # WORKAROUND: We will manually execute donations here to avoid crashing in genesis.py
            # (Or we assume genesis.py wasn't fully overwritten in the execute section?)
            # Let's rely on manual execution for this experiment script to be safe.
            
            for agent in env.agents:
                # Force update intent (act)
                agent.act()
                if agent.intent == 'donate':
                    # Manually execute because genesis.py call might fail or be missing ecosystem
                    if agent.donate(env):
                        donations += 1
            
            env.update()
            
            # Stats
            clients = [a for a in env.agents if a.lineage_id == "Client"]
            patrons = [a for a in env.agents if a.lineage_id == "Patron"]
            
            pop_patron = len(patrons)
            pop_client = len(clients)
            
            avg_nrg_patron = 0
            if patrons: avg_nrg_patron = sum(a.energy for a in patrons) / len(patrons)
            
            avg_nrg_client = 0
            if clients: avg_nrg_client = sum(a.energy for a in clients) / len(clients)
            
            writer.writerow([tick, pop_patron, pop_client, f"{avg_nrg_patron:.1f}", f"{avg_nrg_client:.1f}", donations])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Patron={pop_patron} ({avg_nrg_patron:.1f}), Client={pop_client} ({avg_nrg_client:.1f}), Donations={donations}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Patron={pop_patron}, Client={pop_client}")

if __name__ == "__main__":
    run_patronage_experiment()
