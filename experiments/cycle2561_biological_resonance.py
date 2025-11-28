
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

class Organism:
    def __init__(self, id):
        self.id = id
        # Genome: List of frequencies
        self.genome = [random.uniform(1, 30) for _ in range(3)]
        self.fitness = 0.0
        
    def mutate(self):
        # Change one gene
        idx = random.randint(0, 2)
        self.genome[idx] += random.uniform(-2, 2)
        self.genome[idx] = max(1, self.genome[idx])

def get_fitness(org, target_freqs):
    # Fitness = How close are genes to targets?
    # We check the best match for each target
    total_error = 0
    for t in target_freqs:
        # Find closest gene
        dists = [abs(g - t) for g in org.genome]
        total_error += min(dists)
        
    # Max fitness = 100 - error
    return max(0, 100 - total_error)

def run_bio_experiment():
    print("🧬 CYCLE 2561: THE BIOME - GENETIC RESONANCE")
    print("   (Evolution as Frequency Tuning)")
    
    # 1. The Environment (Hidden Frequencies)
    TARGETS = [13.0, 21.0, 8.0]
    print(f"🌍 Environment Frequencies: {TARGETS}")
    
    # 2. Population
    pop = [Organism(i) for i in range(20)]
    
    duration = 50
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2561_biological_resonance.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["gen", "best_fitness", "best_genome"])
        
        for gen in range(1, duration + 1):
            # Evaluate
            for org in pop:
                org.fitness = get_fitness(org, TARGETS)
                
            # Sort
            pop.sort(key=lambda x: x.fitness, reverse=True)
            best = pop[0]
            
            writer.writerow([gen, f"{best.fitness:.2f}", str([f"{g:.1f}" for g in best.genome])])
            
            if gen % 10 == 0:
                print(f"   Gen {gen}: BestFit={best.fitness:.2f} Genome={[f'{g:.1f}' for g in best.genome]}")
                
            if best.fitness > 99.0:
                print("✨ EVOLUTIONARY RESONANCE ACHIEVED.")
                break
                
            # Selection & Reproduction
            survivors = pop[:5] # Top 5
            new_pop = []
            while len(new_pop) < 20:
                parent = random.choice(survivors)
                child = Organism(len(new_pop))
                child.genome = parent.genome.copy()
                child.mutate()
                new_pop.append(child)
            pop = new_pop

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_bio_experiment()
