
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
    print("CYCLE 2499: THE WENDIGO")
    print("-----------------------")
    
    # Initialize Ecosystem
    # High Prey Capacity to sustain population, Low Predator Capacity to force competition
    ecosystem = Ecosystem(capacity=300, prey_capacity=250, predator_capacity=20)
    
    # Add Prey (200)
    for i in range(200):
        prey = DigitalLifeform(name=f"Prey-{i}")
        prey.is_prey = True
        prey.is_predator = False
        prey.energy = 800
        ecosystem.add_agent(prey)
        
    # Add Predators (10)
    for i in range(10):
        pred = DigitalLifeform(name=f"Wendigo-{i}")
        pred.is_prey = False
        pred.is_predator = True
        pred.energy = 200
        # Randomize Gene 7 (Cannibalism) explicitly to ensure variance
        # 0.0 = Never eat kin, 1.0 = Always eat kin
        while len(pred.genome) < 8: pred.genome.append(0.5)
        ecosystem.add_agent(pred)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2499_wendigo.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_count", "predator_count", "avg_cannibalism", "avg_hunt", "avg_evasion"])
        
        for tick in range(1, 1001):
            ecosystem.update()
            
            # Collect Stats
            prey = [a for a in ecosystem.agents if a.is_prey]
            predators = [a for a in ecosystem.agents if a.is_predator]
            
            prey_count = len(prey)
            pred_count = len(predators)
            
            # Stats
            avg_cannibalism = 0
            avg_hunt = 0
            if predators:
                c_traits = []
                h_traits = []
                for p in predators:
                    while len(p.genome) < 8: p.genome.append(0.5)
                    c_traits.append(p.genome[7])
                    h_traits.append(p.genome[4])
                avg_cannibalism = statistics.mean(c_traits)
                avg_hunt = statistics.mean(h_traits)
                
            avg_evasion = 0
            if prey:
                e_traits = []
                for p in prey:
                    while len(p.genome) < 7: p.genome.append(0.5)
                    e_traits.append(p.genome[6])
                avg_evasion = statistics.mean(e_traits)
            
            writer.writerow([tick, prey_count, pred_count, avg_cannibalism, avg_hunt, avg_evasion])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Pred={pred_count}, Cannibalism={avg_cannibalism:.2f}, Hunt={avg_hunt:.2f}")
                
            if pred_count == 0:
                print("PREDATORS EXTINCT.")
            
            if prey_count == 0:
                print("PREY EXTINCT.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Pred={pred_count}, Cannibalism={avg_cannibalism:.2f}")

if __name__ == "__main__":
    run_cycle()
