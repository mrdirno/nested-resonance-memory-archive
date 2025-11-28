
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
    print("CYCLE 2510: THE VENTURE CAPITALIST (ANGEL INVESTING)")
    print("----------------------------------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem(capacity=100)
    
    # Add Rich Angels (10)
    for i in range(10):
        angel = DigitalLifeform(name=f"Angel-{i}")
        angel.energy = 5000
        while len(angel.genome) < 10: angel.genome.append(0.5)
        angel.genome[5] = 0.1 # Selfish (but invests for profit)
        angel.genome[8] = 0.9 # High Trust
        angel.genome[9] = 0.9 # High Innovation (Smart Money)
        ecosystem.add_agent(angel)
        
    # Add Poor Smart Founders (25)
    for i in range(25):
        founder = DigitalLifeform(name=f"SmartFounder-{i}")
        founder.energy = 10 # Poor! Cannot start without funding (Cost 50)
        while len(founder.genome) < 10: founder.genome.append(0.5)
        founder.genome[5] = 0.5
        founder.genome[8] = 0.9 # High Trust
        founder.genome[9] = 0.9 # High Innovation
        ecosystem.add_agent(founder)
        
    # Add Poor Dumb Workers (25)
    for i in range(25):
        worker = DigitalLifeform(name=f"DumbWorker-{i}")
        worker.energy = 10 # Poor
        while len(worker.genome) < 10: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust
        worker.genome[9] = 0.1 # Low Innovation
        ecosystem.add_agent(worker)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2510_vc.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "rich_angels", "rich_founders", "rich_dumb", "avg_angel_energy", "avg_founder_energy"])
        
        for tick in range(1, 2001):
            ecosystem.update()
            
            # Collect Stats
            agents = ecosystem.agents
            
            angels = [a for a in agents if "Angel" in a.name]
            founders = [a for a in agents if "SmartFounder" in a.name]
            dumb = [a for a in agents if "DumbWorker" in a.name]
            
            # Count who is Rich (Energy > 350)
            rich_angels = len([a for a in angels if a.energy > 350])
            rich_founders = len([a for a in founders if a.energy > 350])
            rich_dumb = len([a for a in dumb if a.energy > 350])
            
            avg_angel_energy = statistics.mean([a.energy for a in angels]) if angels else 0
            avg_founder_energy = statistics.mean([a.energy for a in founders]) if founders else 0
            
            writer.writerow([tick, rich_angels, rich_founders, rich_dumb, avg_angel_energy, avg_founder_energy])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Angels={rich_angels}, Founders={rich_founders}, Dumb={rich_dumb}, AvgAngel={avg_angel_energy:.1f}, AvgFounder={avg_founder_energy:.1f}")
                
            if not angels and not founders:
                print("EXTINCTION.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Angels={rich_angels}, Founders={rich_founders}, Dumb={rich_dumb}")

if __name__ == "__main__":
    run_cycle()
