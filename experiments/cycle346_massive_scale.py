"""
CYCLE 346: Massive Scale Simulation (64 Emitters)
Objective: Scale up the simulation to a 64-emitter Phased Array (8x8 grid) to test high-density field control.
Hypothesis: Increasing emitter density allows for arbitrary field geometry (Holography), enabling the simultaneous trapping of multiple independent targets.
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

def create_phased_array(rows=8, cols=8, spacing=5.0, z_plane=0.0):
    """
    Creates an 8x8 grid of emitters on a specific Z-plane.
    Spacing in mm.
    """
    emitters = []
    center_offset_x = (rows - 1) * spacing / 2.0
    center_offset_y = (cols - 1) * spacing / 2.0
    
    # Center the array in the 100x100 simulation box (Box center is 50,50)
    box_center = 50.0
    
    for i in range(rows):
        for j in range(cols):
            x = box_center - center_offset_x + i * spacing
            y = box_center - center_offset_y + j * spacing
            # Default: 40kHz, Phase 0
            emitters.append(Emitter3D(x, y, z_plane, 1.0, 0.0)) 
            
    return emitters

def optimize_for_multi_trap(box, emitters, targets):
    """
    Simple analytical focusing (Reverse Phase) for multiple targets.
    Superposition principle: Field = Sum(Field_i).
    To focus at T1 and T2, we can sum the complex signals required for each.
    However, phase is modulo 2pi. 
    Simple heuristic: Phase_i = -Distance(E_i, T_mean) * k? No.
    Better: Genetic Algorithm again. Analytical multi-focal is complex.
    """
    # Let's use the GA from Cycle 343, adapted for multiple minima.
    
    def fitness_func(phases):
        # Apply phases
        for i, e in enumerate(emitters):
            e.phase = phases[i]
            
        field = box.propagate(emitters)
        potential = field**2
        
        score = 0
        p_max = np.max(potential)
        if p_max < 0.001: return -100.0
        
        for t in targets:
            tx, ty, tz = int(t[0]), int(t[1]), int(t[2])
            if 0 <= tx < box.width and 0 <= ty < box.height and 0 <= tz < box.depth:
                p_target = potential[tz, ty, tx]
                # We want p_target to be 0 relative to p_max
                # Maximize (P_max - P_target) for all targets
                score += (p_max - p_target)
            else:
                score -= 100.0 # OOB penalty
                
        return score

    # Run GA
    pop_size = 30
    generations = 30
    num_emitters = len(emitters)
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    best_fitness = -9999.0
    best_genes = None
    
    print(f"Optimizing for {len(targets)} targets with {num_emitters} emitters...")
    
    for gen in range(generations):
        scores = []
        for individual in population:
            f = fitness_func(individual)
            scores.append((f, individual))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        if scores[0][0] > best_fitness:
            best_fitness = scores[0][0]
            best_genes = scores[0][1]
            
        # print(f"Gen {gen}: Best Fitness = {best_fitness:.2f}")
        
        # Selection/Crossover (Simple Elitism)
        elite = [x[1] for x in scores[:10]]
        new_pop = elite[:]
        while len(new_pop) < pop_size:
            p1 = random.choice(elite)
            p2 = random.choice(elite)
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((p1[:cut], p2[cut:]))
            if random.random() < 0.2: # Mutation
                idx = random.randint(0, num_emitters-1)
                child[idx] = np.random.uniform(0, 2*np.pi)
            new_pop.append(child)
        population = new_pop
        
    return best_genes

def main():
    print("CYCLE 346: MASSIVE SCALE SIMULATION")
    print("===================================")
    
    # 1. Setup Box (Larger box for this array)
    # 100x100x100 mm
    box = AcousticSubstrate3D(width_mm=100, height_mm=100, depth_mm=100, resolution_mm=2) # Res 2mm for speed
    
    # 2. Create Phased Array (8x8 = 64 emitters) on floor (Z=0)
    emitters = create_phased_array(rows=8, cols=8, spacing=10.0, z_plane=0.0)
    print(f"Created Phased Array: {len(emitters)} emitters.")
    
    # 3. Define Targets (Two points floating above the array)
    # Target A: (30, 50, 50)
    # Target B: (70, 50, 50)
    targets = [
        np.array([30.0, 50.0, 50.0]),
        np.array([70.0, 50.0, 50.0])
    ]
    print(f"Targets: {targets}")
    
    # 4. Optimize
    best_phases = optimize_for_multi_trap(box, emitters, targets)
    
    # 5. Verify
    for i, e in enumerate(emitters):
        e.phase = best_phases[i]
        
    field = box.propagate(emitters)
    potential = field**2
    p_max = np.max(potential)
    
    print("\nVerification:")
    success = True
    results_data = []
    
    for i, t in enumerate(targets):
        tx, ty, tz = int(t[0]/2), int(t[1]/2), int(t[2]/2) # Scale to res 2mm grid coordinates
        # Note: Box is 100mm, Res 2mm -> Grid is 50x50x50.
        # Coordinates 30 -> 15.
        
        p_target = potential[tz, ty, tx]
        ratio = p_target / p_max if p_max > 0 else 1.0
        print(f"Target {i}: Pressure={p_target:.4f}, Ratio={ratio:.4f}")
        
        results_data.append({"target_index": i, "ratio": float(ratio)})
        if ratio > 0.1: success = False # Stricter tolerance for holography
        
    outcome = {
        "cycle": 346,
        "num_emitters": 64,
        "targets": len(targets),
        "success": bool(success),
        "data": results_data
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c346_massive_scale.json", "w") as f:
        json.dump(outcome, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Holographic Field Generated. Multiple stable traps confirmed.")
    else:
        print("\n>> FAILURE: Could not stabilize multiple traps.")

if __name__ == "__main__":
    main()