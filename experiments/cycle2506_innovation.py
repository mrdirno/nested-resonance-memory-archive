"""
Cycle 2506: The Inventor (Gate 134)
Experiment: Innovation and Social Mobility.
Goal: Enable Workers to become Bosses via High-Yield Labor.
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

def run_innovation_experiment():
    print("💡 CYCLE 2506: THE INVENTOR - SOCIAL MOBILITY VIA INNOVATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Capitalists
    for i in range(20):
        agent = DigitalLifeform(name=f"Boss-{i}", lineage_id="Capital")
        agent.energy = 1000 
        # [..., Trust=0.9, Innovation=0.5]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Group B: The Innovators (Poor but Smart)
    # Variable Innovation Gene
    for i in range(180):
        agent = DigitalLifeform(name=f"Inventor-{i}", lineage_id="Labor")
        agent.energy = 50
        # Gene 9 = Innovation (Random 0.1 to 0.9)
        innovation = random.uniform(0.1, 0.99)
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, innovation]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2506_innovation.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_capital", "pop_labor", "nouveaux_riches", "avg_innovation", "avg_nrg_labor", "contracts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            contracts = 0
            nouveaux_riches = 0
            
            employers = []
            job_seekers = []
            
            # Classification Phase
            # Note: Agents switch roles dynamically based on Energy
            # If a Laborer gets > 500 energy, they become 'hire' intent (Capitalist)
            
            for agent in env.agents:
                agent.act() # Update intent
                
                if agent.energy > 500:
                    # Check if this is a former laborer
                    if agent.lineage_id == "Labor":
                        nouveaux_riches += 1
                
                if agent.intent == 'hire':
                    employers.append(agent)
                elif agent.intent == 'seek_work':
                    job_seekers.append(agent)
            
            # Matching Phase
            random.shuffle(employers)
            random.shuffle(job_seekers)
            
            for seeker in job_seekers:
                if not employers: break
                
                boss = random.choice(employers)
                if seeker.work_for_wage(boss):
                    contracts += 1
                    if boss.energy < 500: 
                        if boss in employers: employers.remove(boss)
            
            env.update()
            
            # Stats
            capital_lineage = [a for a in env.agents if a.lineage_id == "Capital"]
            labor_lineage = [a for a in env.agents if a.lineage_id == "Labor"]
            
            avg_innov = 0
            avg_nrg_lab = 0
            
            if labor_lineage:
                avg_innov = sum(a.genome[9] for a in labor_lineage) / len(labor_lineage)
                avg_nrg_lab = sum(a.energy for a in labor_lineage) / len(labor_lineage)
            
            writer.writerow([tick, len(capital_lineage), len(labor_lineage), nouveaux_riches, f"{avg_innov:.3f}", f"{avg_nrg_lab:.1f}", contracts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Cap={len(capital_lineage)}, Lab={len(labor_lineage)}, NewRich={nouveaux_riches}, AvgInnov={avg_innov:.3f}, Jobs={contracts}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: New Rich Count = {nouveaux_riches}")

if __name__ == "__main__":
    run_innovation_experiment()
