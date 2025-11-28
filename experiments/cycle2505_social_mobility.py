
import sys
import os
import csv
import statistics
from pathlib import Path

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def calculate_gini(incomes):
    if not incomes: return 0.0
    sorted_incomes = sorted(incomes)
    n = len(incomes)
    cumulative = 0
    gini_sum = 0
    for i, income in enumerate(sorted_incomes):
        gini_sum += (i + 1) * income
    
    total_income = sum(sorted_incomes)
    if total_income == 0: return 0.0
    
    return (2 * gini_sum) / (n * total_income) - (n + 1) / n

def run_cycle():
    print("CYCLE 2505: THE REVOLUTION (SOCIAL MOBILITY)")
    print("--------------------------------------------")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem(capacity=100)
    
    # Add Rich Bosses (10)
    # High Energy, Low Altruism (Selfish Capitalists)
    for i in range(10):
        boss = DigitalLifeform(name=f"Boss-{i}")
        boss.energy = 5000 # Massive Capital
        while len(boss.genome) < 6: boss.genome.append(0.5)
        boss.genome[5] = 0.1 # Selfish
        boss.genome[8] = 0.9 # High Trust (Willing to hire)
        ecosystem.add_agent(boss)
        
    # Add Poor Workers (50)
    # Low Energy, Avg Altruism
    for i in range(50):
        worker = DigitalLifeform(name=f"Worker-{i}")
        worker.energy = 100 # Increased buffer
        while len(worker.genome) < 6: worker.genome.append(0.5)
        worker.genome[5] = 0.5
        worker.genome[8] = 0.9 # High Trust (Willing to work)
        ecosystem.add_agent(worker)
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2505_social_mobility.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "boss_count", "worker_count", "new_bosses", "gini_coeff"])
        
        for tick in range(1, 2001):
            ecosystem.update()
            
            # Collect Stats
            agents = ecosystem.agents
            bosses = [a for a in agents if a.energy > 350] # Definition of Boss Class
            workers = [a for a in agents if a.energy <= 350]
            
            # Identify Social Mobility
            # Agents named "Worker-X" who are now in the Boss list
            new_bosses = [a for a in bosses if "Worker" in a.name]
            
            # Gini
            energies = [a.energy for a in agents]
            gini = calculate_gini(energies)
            
            writer.writerow([tick, len(bosses), len(workers), len(new_bosses), gini])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Bosses={len(bosses)}, Workers={len(workers)}, NewBosses={len(new_bosses)}, Gini={gini:.2f}")
                
            if not workers and not bosses:
                print("EXTINCTION.")
                break
                
    print("SIMULATION COMPLETE.")
    print(f"Final: Bosses={len(bosses)}, Workers={len(workers)}, NewBosses={len(new_bosses)}")

if __name__ == "__main__":
    run_cycle()
