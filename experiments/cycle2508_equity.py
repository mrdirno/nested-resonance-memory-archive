"""
Cycle 2508: The Shareholder (Gate 136)
Experiment: Equity Compensation.
Goal: Allow Smart Workers to capture the value of their innovation.
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

def run_equity_experiment():
    print("📈 CYCLE 2508: THE SHAREHOLDER - EQUITY COMPENSATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed Capitalists
    for i in range(20):
        agent = DigitalLifeform(name=f"Boss-{i}", lineage_id="Capital")
        agent.energy = 1000 
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, 0.5]
        env.add_agent(agent)
        
    # Seed Laborers (Random Innovation)
    for i in range(180):
        agent = DigitalLifeform(name=f"Worker-{i}", lineage_id="Labor")
        agent.energy = 50
        innovation = random.uniform(0.1, 0.99)
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9, innovation]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2508_equity.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_capital", "pop_labor", "nouveaux_riches", "avg_innovation", "contracts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            contracts = 0
            nouveaux_riches = 0
            
            employers = []
            job_seekers = []
            
            for agent in env.agents:
                agent.act() 
                
                if agent.energy > 500 and agent.lineage_id == "Labor":
                    nouveaux_riches += 1
                
                if agent.intent == 'hire':
                    employers.append(agent)
                elif agent.intent == 'seek_work':
                    job_seekers.append(agent)
            
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
            labor_lineage = [a for a in env.agents if a.lineage_id == "Labor"]
            capital_lineage = [a for a in env.agents if a.lineage_id == "Capital"]
            
            avg_innov = 0
            if labor_lineage:
                avg_innov = sum(a.genome[9] for a in labor_lineage) / len(labor_lineage)
            
            writer.writerow([tick, len(capital_lineage), len(labor_lineage), nouveaux_riches, f"{avg_innov:.3f}", contracts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Lab={len(labor_lineage)}, NewRich={nouveaux_riches}, AvgInnov={avg_innov:.3f}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: New Rich Count = {nouveaux_riches}")

if __name__ == "__main__":
    run_equity_experiment()
