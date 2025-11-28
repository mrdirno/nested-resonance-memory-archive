"""
Cycle 2504: The Industrialist (Gate 132)
Experiment: Wage Labor and Employment.
Goal: Achieve stable coexistence via Symbiosis (Employment).
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

def run_labor_market():
    print("🏭 CYCLE 2504: THE LABOR MARKET - INDUSTRIALIZATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Capitalists (Rich, Hire Intent)
    print("🌱 Seeding The Capitalists...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Boss-{i}", lineage_id="Capital")
        agent.energy = 1000 
        # Low Altruism (0.1) -> They prefer 'hire' over 'donate' in act()
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.1, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Group B: The Workers (Poor, Seek Work Intent)
    print("🌱 Seeding The Workers...")
    for i in range(180):
        agent = DigitalLifeform(name=f"Worker-{i}", lineage_id="Labor")
        agent.energy = 50 # Starvation level
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2504_labor_market.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_boss", "pop_worker", "avg_nrg_boss", "avg_nrg_worker", "contracts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            contracts = 0
            
            # NO FREE INCOME. The Rich must earn yield via labor or they starve too (eventually).
            # Actually, rich start with 1000. Entropy is 5%. They lose 50/tick.
            # They need labor to survive long term.
            
            # Logic Injection: Matching Market
            # We need to match Seekers with Hirers.
            
            bosses = [a for a in env.agents if a.lineage_id == "Capital"]
            workers = [a for a in env.agents if a.lineage_id == "Labor"]
            
            random.shuffle(bosses)
            random.shuffle(workers)
            
            # Simple Matching: One boss can hire multiple workers?
            # Let's iterate workers and try to find a boss.
            
            for w in workers:
                w.act() # Update intent (should be 'seek_work' if energy < 200)
                if w.intent == 'seek_work':
                    # Find a boss with 'hire' intent (or just money)
                    # genesis.py act() sets intent to 'hire' if rich.
                    # But we need to access potential bosses.
                    
                    # Try 3 random bosses
                    potential_employers = random.sample(bosses, min(len(bosses), 3))
                    for b in potential_employers:
                        b.act() # Ensure intent is updated
                        if b.intent == 'hire':
                            if w.work_for_wage(b):
                                contracts += 1
                                break # Job done
            
            env.update()
            
            # Stats
            pop_boss = len([a for a in env.agents if a.lineage_id == "Capital"])
            pop_worker = len([a for a in env.agents if a.lineage_id == "Labor"])
            
            avg_nrg_boss = 0
            if pop_boss: avg_nrg_boss = sum(a.energy for a in env.agents if a.lineage_id == "Capital") / pop_boss
            
            avg_nrg_worker = 0
            if pop_worker: avg_nrg_worker = sum(a.energy for a in env.agents if a.lineage_id == "Labor") / pop_worker
            
            writer.writerow([tick, pop_boss, pop_worker, f"{avg_nrg_boss:.1f}", f"{avg_nrg_worker:.1f}", contracts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Boss={pop_boss} ({avg_nrg_boss:.1f}), Worker={pop_worker} ({avg_nrg_worker:.1f}), Jobs={contracts}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Boss={pop_boss}, Worker={pop_worker}")

if __name__ == "__main__":
    run_labor_market()
