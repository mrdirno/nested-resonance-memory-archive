"""
Cycle 2510: The Venture Capitalist (Gate 138)
Experiment: Investment instead of Loans.
Goal: Rich agents invest in Smart Workers in exchange for Equity.
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

def run_vc_experiment():
    print("🦄 CYCLE 2510: THE VENTURE CAPITALIST - RISK CAPITAL")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Investors (Rich)
    for i in range(20):
        agent = DigitalLifeform(name=f"Investor-{i}", lineage_id="Capital")
        agent.energy = 2000 # Very Rich
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Group B: The Founders (Poor but Smart)
    for i in range(180):
        agent = DigitalLifeform(name=f"Founder-{i}", lineage_id="Labor")
        agent.energy = 50
        innovation = random.uniform(0.1, 0.99)
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, innovation]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2510_venture_capital.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_capital", "pop_labor", "nouveaux_riches", "avg_innov", "investments"])
        
        env.running = True
        
        investments = 0
        
        for tick in range(1, duration + 1):
            
            nouveaux_riches = 0
            
            # Investment Logic (Simulated here for simplicity)
            investors = [a for a in env.agents if a.lineage_id == "Capital"]
            founders = [a for a in env.agents if a.lineage_id == "Labor" and a.energy < 500]
            
            random.shuffle(investors)
            random.shuffle(founders)
            
            for f in founders:
                if not investors: break
                
                # Check innovation
                innov = f.genome[9] if len(f.genome) > 9 else 0
                
                if innov > 0.7: # Pitch Deck: "I'm smart"
                    inv = random.choice(investors)
                    if inv.energy > 1000:
                        # Seed Round
                        investment_amount = 500
                        inv.energy -= investment_amount
                        f.energy += investment_amount
                        investments += 1
                        # print(f"💰 {inv.name} invested in {f.name} (Innov={innov:.2f})")
            
            # Update Count of Successful Founders
            for agent in env.agents:
                if agent.lineage_id == "Labor" and agent.energy > 500:
                    nouveaux_riches += 1
            
            env.update()
            
            # Stats
            capital_lineage = [a for a in env.agents if a.lineage_id == "Capital"]
            labor_lineage = [a for a in env.agents if a.lineage_id == "Labor"]
            
            avg_innov = 0
            if labor_lineage:
                avg_innov = sum(a.genome[9] for a in labor_lineage) / len(labor_lineage)
            
            writer.writerow([tick, len(capital_lineage), len(labor_lineage), nouveaux_riches, f"{avg_innov:.3f}", investments])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Cap={len(capital_lineage)}, Lab={len(labor_lineage)}, NewRich={nouveaux_riches}, Invest={investments}")
            
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: New Rich Count = {nouveaux_riches}")

if __name__ == "__main__":
    run_vc_experiment()
