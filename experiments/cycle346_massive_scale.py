"""
CYCLE 346: Massive Scale Simulation (64 Emitters)
Objective: Scale the simulation to an 8x8 Phased Array and create MULTIPLE traps.
Hypothesis: A higher density array (64 emitters) can support complex geometries (2+ traps).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 3 Pro (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import random

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
# Import GA components or redefine if needed. Redefining for clarity and specific modifications.
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def calculate_fitness_multi(phases, box, emitters, targets):
    """
    Fitness Function for Multiple Targets.
    Fitness = Sum of (Max Pressure - Target Pressure) for all targets.
    We want LOW pressure at ALL target points.
    """
    # Apply phases
    for i, e in enumerate(emitters):
        e.phase = phases[i]
        
    field = box.propagate(emitters)
    potential = field**2
    p_max = np.max(potential)
    
    total_score = 0
    for t in targets:
        tx, ty, tz = int(t[0]), int(t[1]), int(t[2])
        
        # Bounds check
        if not (0 <= tx < box.width and 0 <= ty < box.height and 0 <= tz < box.depth):
            return -1.0
            
        p_target = potential[tz, ty, tx]
        # Score: We want p_target to be small.
        # Contribution = p_max - p_target.
        total_score += (p_max - p_target)
        
    return total_score

def genetic_algorithm_multi(targets, box, emitters, generations=50, pop_size=50):
    """
    GA for Multi-Trap Optimization.
    """
    num_emitters = len(emitters)
    
    # Initialize Population
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    history = []
    
    print(f"Evolution Start: {num_emitters} Emitters, {len(targets)} Targets")
    
    for gen in range(generations):
        scores = []
        for individual in population:
            fitness = calculate_fitness_multi(individual, box, emitters, targets)
            scores.append((fitness, individual))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        best_fitness = scores[0][0]
        best_genes = scores[0][1]
        
        history.append(best_fitness)
        if gen % 10 == 0:
            print(f"Gen {gen}: Best Fitness = {best_fitness:.4f}")
        
        # Selection & Reproduction
        elite_size = int(pop_size * 0.2)
        elite = [x[1] for x in scores[:elite_size]]
        
        new_pop = elite[:]
        while len(new_pop) < pop_size:
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((parent1[:cut], parent2[cut:]))
            
            if random.random() < 0.2: # Mutation
                idx = random.randint(0, num_emitters-1)
                child[idx] = np.random.uniform(0, 2*np.pi)
                
            new_pop.append(child)
            
        population = new_pop
        
    return best_genes, history

def main():
    print("CYCLE 346: MASSIVE SCALE SIMULATION (64 EMITTERS)")
    print("===============================================")
    
    # 1. Setup Environment (Larger Box)
    # 100mm x 100mm x 50mm, 2mm resolution (to keep speed reasonable)
    res = 2
    box = AcousticSubstrate3D(width_mm=100, height_mm=100, depth_mm=50, resolution_mm=res)
    print(f"Volume: {box.width}x{box.height}x{box.depth} voxels")
    
    # 2. 8x8 Emitter Array (Bottom Plane, z=0)
    emitters = []
    spacing = 10 # mm spacing
    start_x = 15
    start_y = 15
    
    for row in range(8):
        for col in range(8):
            x = start_x + (col * spacing)
            y = start_y + (row * spacing)
            z = 0
            emitters.append(Emitter3D(x, y, z, 1.0, 0.0))
            
    print(f"Array Configured: {len(emitters)} Emitters")
    
    # 3. Targets (Two Traps)
    # In mm: (35, 50, 25) and (65, 50, 25)
    # In voxels (res=2): (17, 25, 12) and (32, 25, 12)
    t1_mm = np.array([35, 50, 25])
    t2_mm = np.array([65, 50, 25])
    
    t1_vox = t1_mm / res
    t2_vox = t2_mm / res
    
    targets = [t1_vox, t2_vox]
    print(f"Targets (Voxels): {targets}")
    
    # 4. Run GA
    best_phases, history = genetic_algorithm_multi(targets, box, emitters, generations=50, pop_size=50)
    
    # 5. Verify
    print("\n--- Verifying Solution ---")
    for i, e in enumerate(emitters):
        e.phase = best_phases[i]
        
    field = box.propagate(emitters)
    potential = field**2
    p_max = np.max(potential)
    
    results_data = {}
    success_count = 0
    
    for i, t in enumerate(targets):
        tx, ty, tz = int(t[0]), int(t[1]), int(t[2])
        p_val = potential[tz, ty, tx]
        ratio = p_val / p_max
        print(f"Target {i+1}: Pressure={p_val:.4f}, Ratio={ratio:.4f}")
        
        results_data[f"target_{i+1}"] = {"pressure": float(p_val), "ratio": float(ratio)}
        
        if ratio < 0.1: # <10% max pressure is a node
            success_count += 1
            
    success = (success_count == len(targets))
    
    if success:
        print(">> SUCCESS: Multiple Traps Formed.")
    else:
        print(f">> FAILURE: Only {success_count}/{len(targets)} traps formed.")
        
    # 6. Save Results
    output = {
        "cycle": 346,
        "emitters": 64,
        "targets": len(targets),
        "fitness_history": [float(x) for x in history],
        "target_data": results_data,
        "success": bool(success)
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c346_massive_scale.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
