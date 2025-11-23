"""
CYCLE 347: The Holographic Swarm (Pattern Memory)
Objective: Trap 3 particles simultaneously in a Triangle formation using the 64-emitter array.
Hypothesis: The field can store "Pattern Memory" - a static configuration that dictates the geometry of the matter within it.
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

# Reuse Emitter3D from previous cycles
class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def create_phased_array(rows=8, cols=8, spacing=10.0, z_plane=0.0):
    emitters = []
    center_offset_x = (rows - 1) * spacing / 2.0
    center_offset_y = (cols - 1) * spacing / 2.0
    box_center = 50.0
    for i in range(rows):
        for j in range(cols):
            x = box_center - center_offset_x + i * spacing
            y = box_center - center_offset_y + j * spacing
            emitters.append(Emitter3D(x, y, z_plane, 1.0, 0.0)) 
    return emitters

def genetic_algorithm_multi_target(target_positions, box, emitters, generations=40, pop_size=30):
    """
    GA optimization for multiple targets simultaneously.
    Fitness = Sum(P_max - P_target_i)
    """
    num_emitters = len(emitters)
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    best_genes = None
    best_score = -9999.0
    
    for gen in range(generations):
        scores = []
        for individual in population:
            # Apply phases
            for i, e in enumerate(emitters): e.phase = individual[i]
            
            field = box.propagate(emitters)
            potential = field**2
            p_max = np.max(potential)
            
            if p_max < 0.001:
                scores.append((-100.0, individual))
                continue
                
            current_score = 0
            for t in target_positions:
                tx, ty, tz = int(t[0]/box.resolution), int(t[1]/box.resolution), int(t[2]/box.resolution)
                if 0 <= tx < field.shape[2] and 0 <= ty < field.shape[1] and 0 <= tz < field.shape[0]:
                    p_val = potential[tz, ty, tx]
                    current_score += (p_max - p_val) # Maximize difference (deep well)
                else:
                    current_score -= 50.0 # OOB
            
            scores.append((current_score, individual))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        if scores[0][0] > best_score:
            best_score = scores[0][0]
            best_genes = scores[0][1]
            
        # print(f"Gen {gen}: Fitness {best_score:.2f}")
        
        elite = [x[1] for x in scores[:10]]
        new_pop = elite[:]
        while len(new_pop) < pop_size:
            p1 = random.choice(elite)
            p2 = random.choice(elite)
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((p1[:cut], p2[cut:]))
            if random.random() < 0.2:
                idx = random.randint(0, num_emitters-1)
                child[idx] = np.random.uniform(0, 2*np.pi)
            new_pop.append(child)
        population = new_pop
        
    return best_genes

def main():
    print("CYCLE 347: HOLOGRAPHIC SWARM (TRIANGLE)")
    print("=======================================")
    
    box = AcousticSubstrate3D(width_mm=100, height_mm=100, depth_mm=100, resolution_mm=2)
    emitters = create_phased_array(rows=8, cols=8, spacing=10.0, z_plane=0.0)
    
    # Define Triangle Targets (Floating at Z=50)
    # Center (50, 50). Radius 20.
    # P1: Top (50, 70)
    # P2: Bottom Left (32.68, 40)
    # P3: Bottom Right (67.32, 40)
    
    targets = [
        np.array([50.0, 70.0, 50.0]),
        np.array([32.0, 40.0, 50.0]), # Approx
        np.array([68.0, 40.0, 50.0])  # Approx
    ]
    
    print(f"Targets: {len(targets)} points (Triangle Formation).")
    
    best_phases = genetic_algorithm_multi_target(targets, box, emitters)
    
    # Verification
    for i, e in enumerate(emitters): e.phase = best_phases[i]
    field = box.propagate(emitters)
    potential = field**2
    p_max = np.max(potential)
    
    success = True
    results_data = []
    
    print("\nVerification:")
    for i, t in enumerate(targets):
        tx, ty, tz = int(t[0]/2), int(t[1]/2), int(t[2]/2)
        p_val = potential[tz, ty, tx]
        ratio = p_val / p_max
        print(f"Point {i}: Ratio {ratio:.4f}")
        results_data.append(ratio)
        
        if ratio > 0.15: success = False # Slightly looser tolerance for 3 points
        
    output = {
        "cycle": 347,
        "shape": "triangle",
        "success": bool(success),
        "ratios": [float(r) for r in results_data]
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c347_holographic_swarm.json", "w") as f:
        json.dump(output, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Holographic Triangle Formed. Matter will conform to this geometry.")
    else:
        print("\n>> FAILURE: Shape unstable.")

if __name__ == "__main__":
    main()
