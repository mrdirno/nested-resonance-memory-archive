
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Mind:
    def __init__(self, id):
        self.id = id
        self.state = 'SUSCEPTIBLE' # S, I, R
        self.belief = 0.0
        self.immunity = random.uniform(0.1, 0.9) # Resistance to new ideas
        self.neighbors = []
        
    def interact(self):
        if self.state != 'INFECTED': return
        
        # Broadcast Virus
        virus_strength = 1.0
        
        for neighbor in self.neighbors:
            if neighbor.state == 'SUSCEPTIBLE':
                # Infection Chance = Strength - Immunity
                # Or probabilistic
                chance = virus_strength - neighbor.immunity
                if random.random() < chance:
                    neighbor.state = 'INFECTED'
                    neighbor.belief = 1.0 # Adopt idea
                    
        # Recovery
        if random.random() < 0.1: # 10% chance to recover per tick
            self.state = 'RECOVERED'

def run_virus_experiment():
    print("🦠 CYCLE 2567: THE VIRUS - MEMETIC EPIDEMIOLOGY")
    print("   (Ideas as Pathogens)")
    
    # 1. Build Network (Small World)
    population = [Mind(i) for i in range(100)]
    
    # Link randomly (Avg degree 4)
    for p in population:
        k = random.randint(2, 6)
        targets = random.sample(population, k)
        for t in targets:
            if t != p and t not in p.neighbors:
                p.neighbors.append(t)
                t.neighbors.append(p) # Undirected
                
    # 2. Patient Zero
    patient_zero = population[0]
    patient_zero.state = 'INFECTED'
    print(f"⚠️  Patient Zero: Mind-{patient_zero.id}")
    
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2567_the_virus.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "S", "I", "R"])
        
        for tick in range(1, duration + 1):
            # Update
            # We need to copy state or iterate carefully?
            # Let's just iterate current state. Order matters but it's fine for stochastic sim.
            
            current_infected = [p for p in population if p.state == 'INFECTED']
            for p in current_infected:
                p.interact()
                
            # Count
            s = len([p for p in population if p.state == 'SUSCEPTIBLE'])
            i = len([p for p in population if p.state == 'INFECTED'])
            r = len([p for p in population if p.state == 'RECOVERED'])
            
            writer.writerow([tick, s, i, r])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: S={s} I={i} R={r}")
                
            if i == 0:
                print("✨ EPIDEMIC ENDED.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_virus_experiment()
