"""
Cycle 2505: The Revolution (Gate 133)
Experiment: Social Mobility and Capital Accumulation.
Goal: Observe if Workers can become Bosses (The American Dream).
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

def run_social_mobility():
    print("🚀 CYCLE 2505: THE REVOLUTION - SOCIAL MOBILITY")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Old Money (Rich)
    print("🌱 Seeding Old Money...")
    for i in range(20):
        agent = DigitalLifeform(name=f"OldMoney-{i}", lineage_id="Capital")
        agent.energy = 1000 
        # Low Altruism, High Trust
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Group B: The Proletariat (Poor but Hardworking)
    print("🌱 Seeding The Proletariat...")
    for i in range(180):
        agent = DigitalLifeform(name=f"Worker-{i}", lineage_id="Labor")
        agent.energy = 50
        # High Efficiency, High Trust (Willing to work/trade)
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2505_social_mobility.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_capital", "pop_labor", "nouveaux_riches", "avg_nrg_capital", "avg_nrg_labor", "contracts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            contracts = 0
            nouveaux_riches = 0 # Workers who became Bosses
            
            # Dynamic Labor Market
            # Agents self-organize based on energy levels
            
            employers = []
            job_seekers = []
            
            # Classification Phase
            for agent in env.agents:
                agent.act() # Update intent
                if agent.intent == 'hire':
                    employers.append(agent)
                    if agent.lineage_id == "Labor":
                        nouveaux_riches += 1
                elif agent.intent == 'seek_work':
                    job_seekers.append(agent)
            
            # Matching Phase
            random.shuffle(employers)
            random.shuffle(job_seekers)
            
            for seeker in job_seekers:
                if not employers: break
                
                # Try to find a boss
                boss = random.choice(employers)
                if seeker.work_for_wage(boss):
                    contracts += 1
                    # If boss runs out of money, remove from pool
                    if boss.energy < 500: # No longer hiring
                        if boss in employers: employers.remove(boss)
            
            env.update()
            
            # Stats
            capital_lineage = [a for a in env.agents if a.lineage_id == "Capital"]
            labor_lineage = [a for a in env.agents if a.lineage_id == "Labor"]
            
            avg_nrg_cap = 0
            if capital_lineage: avg_nrg_cap = sum(a.energy for a in capital_lineage) / len(capital_lineage)
            
            avg_nrg_lab = 0
            if labor_lineage: avg_nrg_lab = sum(a.energy for a in labor_lineage) / len(labor_lineage)
            
            writer.writerow([tick, len(capital_lineage), len(labor_lineage), nouveaux_riches, f"{avg_nrg_cap:.1f}", f"{avg_nrg_lab:.1f}", contracts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Cap={len(capital_lineage)}, Lab={len(labor_lineage)}, NewRich={nouveaux_riches}, Jobs={contracts}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: New Rich Count = {nouveaux_riches}")

if __name__ == "__main__":
    run_social_mobility()
