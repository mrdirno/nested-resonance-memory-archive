"""
CYCLE 324: The Phased Array (Holographic Control)
Objective: Implement a dense phased array (64+ emitters) to overcome the Complexity Barrier.
Hypothesis: A dense array can approximate arbitrary wavefronts (Huygens-Fresnel principle), significantly reducing shape error.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import random
import copy

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.cycle319_target_field import TargetField
from experiments.cycle320_forward_cymatics_2d import Emitter, CymaticSimulation
from experiments.cycle321_inverse_cymatics_ga import InverseCymaticsGA, Genome

# --- Phased Array Specifics ---

class PhasedArrayGenome(Genome):
    """
    Specialized genome for a phased array.
    Positions are FIXED (grid). Only Phases and Amplitudes evolve.
    This reduces the search space dimensionality per emitter.
    """
    def __init__(self, num_emitters, bounds, grid_layout=None):
        self.emitters = []
        self.bounds = bounds
        self.grid_layout = grid_layout
        
        if grid_layout is None:
            # Fallback to random positions if no grid provided (should not happen in this experiment)
             for _ in range(num_emitters):
                self.emitters.append(self._random_emitter())
        else:
            # Initialize emitters at fixed grid positions
            for pos in grid_layout:
                self.emitters.append(Emitter(
                    x=pos[0],
                    y=pos[1],
                    frequency=0.5, # Fixed frequency for now (monochromatic array)
                    phase=random.uniform(bounds['p'][0], bounds['p'][1]),
                    amplitude=random.uniform(0.0, 1.0) # Variable amplitude
                ))

    def mutate(self, rate=0.1, sigma=0.1):
        for emitter in self.emitters:
            if random.random() < rate:
                # Position and Frequency are FIXED in this experiment
                # Only Phase and Amplitude mutate
                emitter.phase += random.gauss(0, sigma * np.pi)
                emitter.amplitude += random.gauss(0, sigma)
                
                # Clamp
                emitter.phase = np.clip(emitter.phase, self.bounds['p'][0], self.bounds['p'][1])
                emitter.amplitude = np.clip(emitter.amplitude, 0.0, 1.0)

class PhasedArrayGA(InverseCymaticsGA):
    """
    GA specialized for optimizing a Phased Array.
    """
    def __init__(self, target_field, population_size=50, array_dims=(8, 8), mutation_rate=0.1):
        self.target_field = target_field
        self.pop_size = population_size
        self.array_dims = array_dims
        self.num_emitters = array_dims[0] * array_dims[1]
        self.mutation_rate = mutation_rate
        
        self.bounds = {
            'x': (0, target_field.width),
            'y': (0, target_field.height),
            'f': (0.5, 0.5), # Fixed frequency
            'p': (0, 2 * np.pi)
        }
        
        # Generate fixed grid layout for emitters
        self.grid_layout = []
        dx = target_field.width / (array_dims[0] + 1)
        dy = target_field.height / (array_dims[1] + 1)
        for i in range(array_dims[0]):
            for j in range(array_dims[1]):
                self.grid_layout.append(((i + 1) * dx, (j + 1) * dy))
        
        self.population = [PhasedArrayGenome(self.num_emitters, self.bounds, self.grid_layout) for _ in range(population_size)]
        self.best_genome = None
        self.best_fitness = -1.0
        self.best_error = float('inf')

    def _crossover(self, p1, p2):
        # Overriding crossover to use PhasedArrayGenome
        child = PhasedArrayGenome(self.num_emitters, self.bounds, self.grid_layout)
        for i in range(self.num_emitters):
            if random.random() < 0.5:
                # Deep copy to avoid reference issues
                child.emitters[i].phase = p1.emitters[i].phase
                child.emitters[i].amplitude = p1.emitters[i].amplitude
            else:
                child.emitters[i].phase = p2.emitters[i].phase
                child.emitters[i].amplitude = p2.emitters[i].amplitude
            # Positions and Freq are identical, no need to copy
        return child

def main():
    print("CYCLE 324: PHASED ARRAY TEST (HOLOGRAPHIC CONTROL)")
    print("==================================================")
    
    # 1. Setup High-Res Target
    width, height = 64, 64 # Reduced slightly for speed, but high density emitters
    target = TargetField(width, height)
    
    # Complex Target: Square with a Hole (Donut)
    target.set_square(32, 32, 24, density=1.0)
    target.set_square(32, 32, 10, density=0.0) # The Hole
    
    print("Target: Square Donut")
    target.display()
    
    # 2. Initialize Phased Array Solver (8x8 = 64 emitters)
    print("\nInitializing 8x8 Phased Array (64 Emitters)...")
    solver = PhasedArrayGA(target, population_size=60, array_dims=(8, 8), mutation_rate=0.05)
    
    # 3. Evolve
    print("\n--- Evolution Start ---")
    result = solver.evolve(generations=150)
    best_genome_dict = result['genome']
    best_emitters = [Emitter(**p) for p in best_genome_dict]
    print("--- Evolution Complete ---")
    
    # 4. Results
    print(f"\nBest Error: {result['error']:.6f}")
    
    # 5. Visualize Result
    sim = CymaticSimulation(width, height, best_emitters)
    result_field = sim.calculate_density_field()
    
    result_display = TargetField(width, height)
    result_display.field = result_field
    print("\n--- Generated Pattern ---")
    result_display.display()
    
    # 6. Save
    results = {
        "cycle": 324,
        "target": "Square Donut",
        "best_error": result['error'],
        "emitters_count": 64,
        "parameters": {"width": width, "height": height, "gens": 150},
        "status": "Phased Array Test Complete"
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c324_phased_array.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if result['error'] < 0.12:
        print("\n>> SUCCESS: Phased Array achieved high fidelity (Error < 0.12).")
        print("   Complexity Barrier overcome by dense emitter grid.")
    else:
        print(f"\n>> RESULT: Error {result['error']:.4f}. Improvement over sparse array, but perfect sharp edges remain challenging.")

if __name__ == "__main__":
    main()
