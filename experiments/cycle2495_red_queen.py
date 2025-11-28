
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
    print("CYCLE 2495: THE RED QUEEN")
    print("-------------------------")
    
    # Initialize Ecosystem
    # "Nuclear Option": Massive Prey advantage to prevent extinction
    ecosystem = Ecosystem(capacity=300, prey_capacity=250, predator_capacity=15)
    
    # Add Prey (200)
    for i in range(200):
        prey = DigitalLifeform(name=f"Prey-{i}")
        prey.is_prey = True
        prey.is_predator = False
        prey.energy = 800 # Boosted start
        ecosystem.add_agent(prey)
        
    # Add Predators (5)
    for i in range(5):
        pred = DigitalLifeform(name=f"Hunter-{i}")
        pred.is_prey = False
        pred.is_predator = True
        pred.energy = 100 # Starving start
        ecosystem.add_agent(pred)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2495_red_queen.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_count", "predator_count", "avg_hunt_skill", "avg_evasion_skill"])
        
        for tick in range(1, 1001):
            ecosystem.update()
            
            # Collect Stats
            prey = [a for a in ecosystem.agents if a.is_prey]
            predators = [a for a in ecosystem.agents if a.is_predator]
            
            prey_count = len(prey)
            pred_count = len(predators)
            
            # Gene 4 = Hunt, Gene 6 = Evasion
            # Ensure genome is long enough before accessing
            avg_hunt = 0
            if predators:
                hunt_skills = []
                for p in predators:
                    while len(p.genome) < 5: p.genome.append(0.5)
                    hunt_skills.append(p.genome[4])
                avg_hunt = statistics.mean(hunt_skills)
                
            avg_evasion = 0
            if prey:
                evasion_skills = []
                for p in prey:
                    while len(p.genome) < 7: p.genome.append(0.5)
                    evasion_skills.append(p.genome[6])
                avg_evasion = statistics.mean(evasion_skills)
            
            writer.writerow([tick, prey_count, pred_count, avg_hunt, avg_evasion])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Prey={prey_count}, Pred={pred_count}, Hunt={avg_hunt:.2f}, Evasion={avg_evasion:.2f}")
                
            if pred_count == 0:
                print("PREDATORS EXTINCT.")
            
            if prey_count == 0:
                print("PREY EXTINCT.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Prey={prey_count}, Pred={pred_count}, Hunt={avg_hunt:.2f}, Evasion={avg_evasion:.2f}")

if __name__ == "__main__":
    run_cycle()
