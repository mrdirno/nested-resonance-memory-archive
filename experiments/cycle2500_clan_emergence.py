
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
    print("CYCLE 2500: THE EMERGENCE OF CLANS")
    print("----------------------------------")
    
    # Initialize Ecosystem
    # "Nuclear Option": Massive Prey advantage to prevent extinction
    ecosystem = Ecosystem(capacity=300, prey_capacity=250, predator_capacity=20)
    
    # Add Prey (200)
    for i in range(200):
        prey = DigitalLifeform(name=f"Prey-{i}")
        prey.is_prey = True
        prey.is_predator = False
        prey.energy = 2000 # God Mode
        ecosystem.add_agent(prey)
        
    # Add Predator Clans (4 Clans x 5 Members = 20 Predators)
    clans = ["Clan-A", "Clan-B", "Clan-C", "Clan-D"]
    for clan_name in clans:
        for i in range(5):
            pred = DigitalLifeform(name=f"{clan_name}-{i}", lineage_id=clan_name)
            pred.is_prey = False
            pred.is_predator = True
            pred.energy = 50 # Starving start
            
            # Gene 5 = Altruism. 
            # Seed Clans with different Altruism levels to test hypothesis
            # Clan-A: High Altruism (The Cooperators)
            # Clan-D: Low Altruism (The Selfish)
            if clan_name == "Clan-A":
                while len(pred.genome) < 6: pred.genome.append(0.5)
                pred.genome[5] = 0.9 # Very Altruistic
            elif clan_name == "Clan-D":
                while len(pred.genome) < 6: pred.genome.append(0.5)
                pred.genome[5] = 0.1 # Very Selfish
            else:
                # Random
                while len(pred.genome) < 6: pred.genome.append(0.5)
                
            ecosystem.add_agent(pred)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2500_clan_emergence.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_count", "clan_a_count", "clan_b_count", "clan_c_count", "clan_d_count", "avg_altruism"])
        
        for tick in range(1, 1001):
            ecosystem.update()
            
            # Collect Stats
            prey = [a for a in ecosystem.agents if a.is_prey]
            predators = [a for a in ecosystem.agents if a.is_predator]
            
            prey_count = len(prey)
            
            clan_counts = {c: 0 for c in clans}
            altruism_scores = []
            
            for p in predators:
                # Check lineage
                lid = p.lineage_id
                # Handle mutations (new clans)
                if lid in clan_counts:
                    clan_counts[lid] += 1
                
                while len(p.genome) < 6: p.genome.append(0.5)
                altruism_scores.append(p.genome[5])
            
            avg_altruism = statistics.mean(altruism_scores) if altruism_scores else 0
            
            writer.writerow([tick, prey_count, clan_counts["Clan-A"], clan_counts["Clan-B"], clan_counts["Clan-C"], clan_counts["Clan-D"], avg_altruism])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: A={clan_counts['Clan-A']}, B={clan_counts['Clan-B']}, C={clan_counts['Clan-C']}, D={clan_counts['Clan-D']}, Alt={avg_altruism:.2f}")
                
            if not predators:
                print("PREDATORS EXTINCT.")
            
            if prey_count == 0:
                print("PREY EXTINCT.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: A={clan_counts['Clan-A']}, D={clan_counts['Clan-D']}")

if __name__ == "__main__":
    run_cycle()
