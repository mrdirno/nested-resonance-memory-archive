
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
    print("CYCLE 2494: THE AWAKENING OF THE HUNTERS")
    print("----------------------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem()
    
    # Add Prey (95)
    for i in range(95):
        prey = DigitalLifeform(name=f"Prey-{i}")
        prey.is_prey = True
        prey.is_predator = False
        ecosystem.add_agent(prey)
        
    # Add Predators (5)
    for i in range(5):
        pred = DigitalLifeform(name=f"Hunter-{i}")
        pred.is_prey = False
        pred.is_predator = True
        pred.energy = 200 # Starting energy
        ecosystem.add_agent(pred)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2494_predator_fix.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_count", "predator_count", "avg_prey_energy", "avg_pred_energy"])
        
        for tick in range(1, 1001):
            ecosystem.update()
            
            # Collect Stats
            prey = [a for a in ecosystem.agents if a.is_prey]
            predators = [a for a in ecosystem.agents if a.is_predator]
            
            prey_count = len(prey)
            pred_count = len(predators)
            
            avg_prey_e = statistics.mean([a.energy for a in prey]) if prey else 0
            avg_pred_e = statistics.mean([a.energy for a in predators]) if predators else 0
            
            writer.writerow([tick, prey_count, pred_count, avg_prey_e, avg_pred_e])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Prey={prey_count}, Pred={pred_count}, AvgPredE={avg_pred_e:.1f}")
                
            if pred_count == 0:
                print("PREDATORS EXTINCT.")
                # break # Don't break, let's see if prey explode
            
            if prey_count == 0:
                print("PREY EXTINCT.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Prey={prey_count}, Pred={pred_count}")

if __name__ == "__main__":
    run_cycle()
