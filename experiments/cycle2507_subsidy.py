
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
    print("CYCLE 2507: THE SUBSIDY (STATE-FUNDED INNOVATION)")
    print("-------------------------------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem(capacity=100)
    
    # Add Rich Bosses (10)
    for i in range(10):
        boss = DigitalLifeform(name=f"Boss-{i}")
        boss.energy = 5000
        while len(boss.genome) < 10: boss.genome.append(0.5)
        boss.genome[5] = 0.1 # Selfish
        boss.genome[8] = 0.9 # High Trust (Willing to hire)
        ecosystem.add_agent(boss)
        
    # Add Smart Workers (25)
    for i in range(25):
        worker = DigitalLifeform(name=f"SmartWorker-{i}")
        worker.energy = 100
        while len(worker.genome) < 10: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust
        worker.genome[9] = 0.9 # High Innovation
        ecosystem.add_agent(worker)
        
    # Add Dumb Workers (25)
    for i in range(25):
        worker = DigitalLifeform(name=f"DumbWorker-{i}")
        worker.energy = 100
        while len(worker.genome) < 10: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust
        worker.genome[9] = 0.1 # Low Innovation
        ecosystem.add_agent(worker)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2507_subsidy.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "smart_bosses", "dumb_bosses", "avg_smart_energy", "avg_dumb_energy"])
        
        for tick in range(1, 2001):
            ecosystem.update()
            
            # Collect Stats
            agents = ecosystem.agents
            
            smart_workers = [a for a in agents if "SmartWorker" in a.name]
            dumb_workers = [a for a in agents if "DumbWorker" in a.name]
            
            # Count who became Bosses (Energy > 350)
            smart_bosses = len([a for a in smart_workers if a.energy > 350])
            dumb_bosses = len([a for a in dumb_workers if a.energy > 350])
            
            avg_smart_energy = statistics.mean([a.energy for a in smart_workers]) if smart_workers else 0
            avg_dumb_energy = statistics.mean([a.energy for a in dumb_workers]) if dumb_workers else 0
            
            writer.writerow([tick, smart_bosses, dumb_bosses, avg_smart_energy, avg_dumb_energy])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: SmartBosses={smart_bosses}, DumbBosses={dumb_bosses}, AvgSmart={avg_smart_energy:.1f}, AvgDumb={avg_dumb_energy:.1f}")
                
            if not smart_workers and not dumb_workers:
                print("EXTINCTION.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: SmartBosses={smart_bosses}, DumbBosses={dumb_bosses}")

if __name__ == "__main__":
    run_cycle()
