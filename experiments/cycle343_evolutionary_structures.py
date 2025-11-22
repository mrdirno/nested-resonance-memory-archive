"""
CYCLE 343: Evolutionary Acoustic Structures (Genetic Algorithm)
Objective: Evolve a phase pattern that creates a focal point (trap) at a target location
           WITHOUT using the analytical solver.
Hypothesis: The system can "learn" physics through trial and error (Evolution).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 3 Pro (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import random
import copy

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D

class Emitter:
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.frequency = frequency
        self.phase = phase
        self.amplitude = amplitude

class GeneticOptimizer:
    def __init__(self, target_pos, substrate, emitters_config, pop_size=50, mutation_rate=0.1):
        self.target_pos = target_pos # (x, y, z) tuple
        self.substrate = substrate
        self.emitters_config = emitters_config # List of dicts with fixed pos/freq
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = [] # List of gene lists (phases)
        
        self.init_population()
        
    def init_population(self):
        """Initialize random phases for each emitter."""
        num_emitters = len(self.emitters_config)
        for _ in range(self.pop_size):
            # Random phases between 0 and 2pi
            genes = [random.uniform(0, 2*np.pi) for _ in range(num_emitters)]
            self.population.append(genes)
            
    def evaluate_fitness(self, genes):
        """
        Calculate fitness of a gene set.
        Fitness = Trap Depth = (Avg Neighbor Potential) - (Target Potential)
        We want Target to be 0 (Node) and Neighbors to be High (Walls).
        """
        # 1. Configure Emitters with Genes
        emitters = []
        for i, config in enumerate(self.emitters_config):
            e = Emitter(
                x=config['x'], y=config['y'], z=config['z'],
                frequency=config['freq'],
                phase=genes[i],
                amplitude=config['amp']
            )
            emitters.append(e)
            
        # 2. Run Physics Simulation
        field = self.substrate.propagate(emitters)
        potential = field**2
        
        # 3. Measure at Target
        tx, ty, tz = self.target_pos
        
        # Ensure bounds
        if not (0 < tx < self.substrate.width-1 and 
                0 < ty < self.substrate.height-1 and 
                0 < tz < self.substrate.depth-1):
            return -1.0 # Invalid target
            
        target_val = potential[tz, ty, tx]
        
        # 4. Measure Neighbors (6-connectivity)
        neighbors = [
            potential[tz+1, ty, tx], potential[tz-1, ty, tx],
            potential[tz, ty+1, tx], potential[tz, ty-1, tx],
            potential[tz, ty, tx+1], potential[tz, ty, tx-1]
        ]
        avg_neighbor = sum(neighbors) / len(neighbors)
        
        # Fitness: Maximize contrast
        # If target is node (0) and neighbors are high (1), fitness is 1.
        # If target is antinode (1) and neighbors are low (0), fitness is -1.
        fitness = avg_neighbor - target_val
        
        return fitness

    def evolve(self, generations=50):
        best_history = []
        
        print(f"Starting Evolution: {self.pop_size} individuals, {generations} generations")
        
        for gen in range(generations):
            # 1. Evaluate all
            scores = []
            for genes in self.population:
                fit = self.evaluate_fitness(genes)
                scores.append((fit, genes))
            
            # Sort descending (higher fitness is better)
            scores.sort(key=lambda x: x[0], reverse=True)
            
            best_fit = scores[0][0]
            best_history.append(best_fit)
            
            if gen % 10 == 0:
                print(f"Gen {gen}: Best Fitness = {best_fit:.4f}")
                
            # 2. Selection (Top 20%)
            top_count = int(self.pop_size * 0.2)
            survivors = scores[:top_count]
            
            # 3. Reproduction
            new_pop = [s[1] for s in survivors] # Keep elites
            
            while len(new_pop) < self.pop_size:
                # Tournament Selection for parents
                parent_a = random.choice(survivors)[1]
                parent_b = random.choice(survivors)[1]
                
                # Crossover (Uniform)
                child = []
                for i in range(len(parent_a)):
                    if random.random() > 0.5:
                        child.append(parent_a[i])
                    else:
                        child.append(parent_b[i])
                        
                # Mutation
                for i in range(len(child)):
                    if random.random() < self.mutation_rate:
                        # Add small noise or flip
                        child[i] += random.gauss(0, 0.5) # Gaussian mutation
                        child[i] %= (2 * np.pi) # Wrap phase
                        
                new_pop.append(child)
                
            self.population = new_pop
            
        return best_history, scores[0][1] # Return history and best genes

def main():
    print("CYCLE 343: EVOLUTIONARY ACOUSTIC STRUCTURES")
    print("===========================================")
    
    # 1. Setup Environment
    box = AcousticSubstrate3D(width_mm=50, height_mm=50, depth_mm=50, resolution_mm=2) # Lower res for speed
    print(f"Simulation Volume: {box.width}x{box.height}x{box.depth} voxels")
    
    # 2. Configure Emitters (Fixed Positions)
    mid_w = box.width * 2 # mm
    mid_h = box.height * 2
    mid_d = box.depth * 2
    # Wait, resolution is 2mm. Width is 25 pixels.
    # Emitter positions are in mm.
    
    # Let's use the same setup as Cycle 337 but scaled to mm
    # 6 Emitters
    emitters_config = [
        {'x': 25, 'y': 25, 'z': 0,  'freq': 1.0, 'amp': 1.0}, # Top
        {'x': 25, 'y': 25, 'z': 50, 'freq': 1.0, 'amp': 1.0}, # Bottom
        {'x': 0,  'y': 25, 'z': 25, 'freq': 1.0, 'amp': 1.0}, # Left
        {'x': 50, 'y': 25, 'z': 25, 'freq': 1.0, 'amp': 1.0}, # Right
        {'x': 25, 'y': 0,  'z': 25, 'freq': 1.0, 'amp': 1.0}, # Front
        {'x': 25, 'y': 50, 'z': 25, 'freq': 1.0, 'amp': 1.0}  # Back
    ]
    
    # 3. Target: Center
    # Grid coords: 25mm / 2mm = 12.5 -> 12
    target_pos = (12, 12, 12)
    print(f"Target Voxel: {target_pos}")
    
    # 4. Run Evolution
    optimizer = GeneticOptimizer(target_pos, box, emitters_config, pop_size=50, mutation_rate=0.1)
    history, best_genes = optimizer.evolve(generations=50)
    
    print(f"\nFinal Best Fitness: {history[-1]:.4f}")
    print("Best Genes (Phases):")
    print([f"{p:.2f}" for p in best_genes])
    
    # 5. Verify Learning
    improvement = history[-1] - history[0]
    print(f"Fitness Improvement: {improvement:.4f}")
    
    if improvement > 0.5:
        print(">> SUCCESS: System evolved a trap.")
    else:
        print(">> FAILURE: Evolution stalled.")
        
    # 6. Save Results
    results = {
        "cycle": 343,
        "generations": 50,
        "fitness_history": [float(x) for x in history],
        "best_genes": [float(x) for x in best_genes],
        "success": bool(improvement > 0.5)
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c343_evolution.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
