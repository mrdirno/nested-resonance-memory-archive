
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
    print("CYCLE 2503: THE WELFARE STATE")
    print("-----------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem(capacity=100)
    
    # Add Rich Philanthropists (10)
    # High Energy, High Altruism
    for i in range(10):
        rich = DigitalLifeform(name=f"Rich-{i}")
        rich.energy = 2000
        while len(rich.genome) < 6: rich.genome.append(0.5)
        rich.genome[5] = 0.95 # Extremely Altruistic
        rich.genome[3] = 0.8 # Good at foraging (maintaining wealth)
        ecosystem.add_agent(rich)
        
    # Add Poor Dependents (50)
    # Low Energy, Avg Altruism, Poor Foraging
    for i in range(50):
        poor = DigitalLifeform(name=f"Poor-{i}")
        poor.energy = 50 # Starving
        while len(poor.genome) < 6: poor.genome.append(0.5)
        poor.genome[5] = 0.5
        poor.genome[3] = 0.1 # Bad at foraging (dependent)
        ecosystem.add_agent(poor)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2503_patronage.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "rich_count", "poor_count", "avg_poor_energy"])
        
        for tick in range(1, 501):
            ecosystem.update()
            
            # Collect Stats
            rich_agents = [a for a in ecosystem.agents if "Rich" in a.name]
            poor_agents = [a for a in ecosystem.agents if "Poor" in a.name]
            
            rich_count = len(rich_agents)
            poor_count = len(poor_agents)
            
            avg_poor_energy = statistics.mean([a.energy for a in poor_agents]) if poor_agents else 0
            
            writer.writerow([tick, rich_count, poor_count, avg_poor_energy])
            
            if tick % 50 == 0:
                print(f"Tick {tick}: Rich={rich_count}, Poor={poor_count}, AvgPoorEnergy={avg_poor_energy:.2f}")
                
            if poor_count == 0:
                print("ALL POOR DIED.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Rich={len(rich_agents)}, Poor={len(poor_agents)}")

if __name__ == "__main__":
    run_cycle()
