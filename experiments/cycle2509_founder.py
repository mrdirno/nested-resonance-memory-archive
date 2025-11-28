
import sys
import os
import csv
import statistics
from pathlib import Path

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_cycle():
    print("CYCLE 2509: THE FOUNDER (STARTUP MODE)")
    print("--------------------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem(capacity=100)
    
    # Add Old Money Bosses (10)
    for i in range(10):
        boss = DigitalLifeform(name=f"OldMoney-{i}")
        boss.energy = 5000
        while len(boss.genome) < 10: boss.genome.append(0.5)
        boss.genome[5] = 0.1 # Selfish
        boss.genome[8] = 0.9 # High Trust
        boss.genome[9] = 0.1 # Low Innovation (Inherited Wealth)
        ecosystem.add_agent(boss)
        
    # Add Smart Founders (25)
    for i in range(25):
        worker = DigitalLifeform(name=f"SmartFounder-{i}")
        worker.energy = 100
        while len(worker.genome) < 10: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust
        worker.genome[9] = 0.9 # High Innovation (Will attempt Startup)
        ecosystem.add_agent(worker)
        
    # Add Dumb Workers (25)
    for i in range(25):
        worker = DigitalLifeform(name=f"DumbWorker-{i}")
        worker.energy = 100
        while len(worker.genome) < 10: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust
        worker.genome[9] = 0.1 # Low Innovation (Will seek work)
        ecosystem.add_agent(worker)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2509_founder.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "old_money", "smart_bosses", "dumb_bosses", "avg_smart_energy", "avg_dumb_energy"])
        
        for tick in range(1, 2001):
            ecosystem.update()
            
            # Collect Stats
            agents = ecosystem.agents
            
            old_money = [a for a in agents if "OldMoney" in a.name]
            smart_founders = [a for a in agents if "SmartFounder" in a.name]
            dumb_workers = [a for a in agents if "DumbWorker" in a.name]
            
            # Count who is Rich (Energy > 350)
            rich_old_money = len([a for a in old_money if a.energy > 350])
            rich_founders = len([a for a in smart_founders if a.energy > 350])
            rich_dumb = len([a for a in dumb_workers if a.energy > 350])
            
            avg_smart_energy = statistics.mean([a.energy for a in smart_founders]) if smart_founders else 0
            avg_dumb_energy = statistics.mean([a.energy for a in dumb_workers]) if dumb_workers else 0
            
            writer.writerow([tick, rich_old_money, rich_founders, rich_dumb, avg_smart_energy, avg_dumb_energy])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: OldMoney={rich_old_money}, Founders={rich_founders}, DumbRich={rich_dumb}, AvgSmart={avg_smart_energy:.1f}")
                
            if not smart_founders and not dumb_workers:
                print("EXTINCTION.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: OldMoney={rich_old_money}, Founders={rich_founders}, DumbRich={rich_dumb}")

if __name__ == "__main__":
    run_cycle()
