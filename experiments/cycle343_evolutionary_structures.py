"""
CYCLE 343: Evolutionary Acoustic Structures (Genetic Algorithm)
Objective: Evolve a trap at a target location *without* using the analytical solver.
Hypothesis: A Genetic Algorithm can discover the correct phase delays for an arbitrary target, effectively "learning physics" through trial and error.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import random

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def calculate_fitness(phases, box, emitters, target_pos):
    """
    Fitness Function:
    We want a PRESSURE NODE (Minimum P^2) at the target location.
    However, we also want High Pressure *around* it (Confinement).
    So, Fitness = (Avg Pressure on Shell) - (Pressure at Target).
    Actually, for simple levitation, let's just maximize "Trappiness".
    Gorkov potential U is proportional to p^2.
    So we want to minimize p^2 at target.
    But trivial solution is p=0 everywhere (Silence).
    So we must enforce amplitude constraint or maximize gradient.
    Let's try: Maximize (P_max - P_target).
    """
    # Apply phases
    for i, e in enumerate(emitters):
        e.phase = phases[i]
        
    field = box.propagate(emitters)
    potential = field**2
    
    tx, ty, tz = int(target_pos[0]), int(target_pos[1]), int(target_pos[2])
    
    # Bounds check
    if not (0 <= tx < box.width and 0 <= ty < box.height and 0 <= tz < box.depth):
        return -1.0 # Out of bounds
        
    p_target = potential[tz, ty, tx]
    p_max = np.max(potential) # Global max pressure
    
    # Fitness: Max pressure in system should be high (loud), pressure at target should be low (quiet).
    # This ensures we have a standing wave, not silence.
    return p_max - p_target

def genetic_algorithm(target_pos, box, emitters, generations=50, pop_size=20):
    """
    Simple GA to find optimal phases [phi_1, ..., phi_N].
    """
    num_emitters = len(emitters)
    
    # Initialize Population (Random Phases 0..2pi)
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    history = []
    
    for gen in range(generations):
        # Evaluate Fitness
        scores = []
        for individual in population:
            fitness = calculate_fitness(individual, box, emitters, target_pos)
            scores.append((fitness, individual))
            
        # Sort by fitness (High is good)
        scores.sort(key=lambda x: x[0], reverse=True)
        best_fitness = scores[0][0]
        best_genes = scores[0][1]
        
        history.append(best_fitness)
        print(f"Gen {gen}: Best Fitness = {best_fitness:.4f}")
        
        # Selection (Top 20%)
        elite_size = int(pop_size * 0.2)
        elite = [x[1] for x in scores[:elite_size]]
        
        # Crossover & Mutation
        new_pop = elite[:]
        while len(new_pop) < pop_size:
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            # Crossover point
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((parent1[:cut], parent2[cut:]))
            
            # Mutation (10% chance per gene)
            if random.random() < 0.3: # High mutation for exploration
                idx = random.randint(0, num_emitters-1)
                child[idx] = np.random.uniform(0, 2*np.pi)
                
            new_pop.append(child)
            
        population = new_pop
        
    return best_genes, history

def main():
    print("CYCLE 343: EVOLUTIONARY ACOUSTIC STRUCTURES")
    print("==========================================")
    
    # 1. Setup
    box = AcousticSubstrate3D(width_mm=50, height_mm=50, depth_mm=50, resolution_mm=1)
    mid = 25.0
    
    # 6-Axis Emitter Array
    emitters = [
        Emitter3D(mid, mid, 0, 1.0, 0.0), Emitter3D(mid, mid, 50, 1.0, 0.0),
        Emitter3D(0, mid, mid, 1.0, 0.0), Emitter3D(50, mid, mid, 1.0, 0.0),
        Emitter3D(mid, 0, mid, 1.0, 0.0), Emitter3D(mid, 50, mid, 1.0, 0.0)
    ]
    
    # Target: Off-center location (15, 25, 25)
    target = np.array([15.0, 25.0, 25.0])
    print(f"Target Location: {target}")
    
    # 2. Run GA
    print("\n--- Starting Evolution ---")
    best_phases, fitness_history = genetic_algorithm(target, box, emitters)
    
    # 3. Verification
    print("\n--- Verifying Solution ---")
    for i, e in enumerate(emitters):
        e.phase = best_phases[i]
        
    field = box.propagate(emitters)
    potential = field**2
    
    tx, ty, tz = int(target[0]), int(target[1]), int(target[2])
    p_target = potential[tz, ty, tx]
    p_max = np.max(potential)
    
    print(f"Pressure at Target: {p_target:.4f}")
    print(f"Max Pressure in Box: {p_max:.4f}")
    print(f"Ratio (Target/Max): {p_target/p_max:.4f}")
    
    success = (p_target < 0.1 * p_max) # Less than 10% of max pressure is a decent node
    
    results = {
        "cycle": 343,
        "generations": 50,
        "fitness_history": [float(x) for x in fitness_history],
        "final_phases": [float(x) for x in best_phases],
        "success": bool(success)
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c343_evolutionary_structures.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Evolution discovered a valid trap configuration.")
    else:
        print("\n>> FAILURE: Evolution failed to find a trap.")

if __name__ == "__main__":
    main()