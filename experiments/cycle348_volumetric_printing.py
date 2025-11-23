"""
CYCLE 348: Volumetric 3D Printing (The Matter Compiler)
Objective: Trap particles simultaneously at the 8 corners of a cube in 3D space.
Hypothesis: The high-density emitter array can create complex 3D holographic fields to form stable volumetric patterns. This is the foundation of "Matter Compilation."
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

def create_phased_array_6_sides(box_dim=100.0, emitter_spacing=10.0, num_emitters_per_side=8):
    """
    Creates emitters on all 6 sides of a cube, for full 3D control.
    Total emitters will be 6 * num_emitters_per_side * num_emitters_per_side.
    For num_emitters_per_side=8, this is 6 * 8 * 8 = 384 emitters.
    """
    emitters = []
    
    # Emitters for one face (e.g., z=0 face)
    def create_face_emitters(fixed_coord, axis1, axis2, val1, val2, orientation):
        center_offset1 = (num_emitters_per_side - 1) * emitter_spacing / 2.0
        center_offset2 = (num_emitters_per_side - 1) * emitter_spacing / 2.0
        
        box_center = box_dim / 2.0
        
        for i in range(num_emitters_per_side):
            for j in range(num_emitters_per_side):
                coord1 = box_center - center_offset1 + i * emitter_spacing
                coord2 = box_center - center_offset2 + j * emitter_spacing
                
                if orientation == 'z0':
                    emitters.append(Emitter3D(coord1, coord2, fixed_coord, 1.0, 0.0))
                elif orientation == 'z1':
                    emitters.append(Emitter3D(coord1, coord2, fixed_coord, 1.0, 0.0))
                elif orientation == 'x0':
                    emitters.append(Emitter3D(fixed_coord, coord1, coord2, 1.0, 0.0))
                elif orientation == 'x1':
                    emitters.append(Emitter3D(fixed_coord, coord1, coord2, 1.0, 0.0))
                elif orientation == 'y0':
                    emitters.append(Emitter3D(coord1, fixed_coord, coord2, 1.0, 0.0))
                elif orientation == 'y1':
                    emitters.append(Emitter3D(coord1, fixed_coord, coord2, 1.0, 0.0))

    # Face Z=0
    create_face_emitters(0.0, 'x', 'y', 'x', 'y', 'z0')
    # Face Z=box_dim
    create_face_emitters(box_dim, 'x', 'y', 'x', 'y', 'z1')
    # Face X=0
    create_face_emitters(0.0, 'y', 'z', 'y', 'z', 'x0')
    # Face X=box_dim
    create_face_emitters(box_dim, 'y', 'z', 'y', 'z', 'x1')
    # Face Y=0
    create_face_emitters(0.0, 'x', 'z', 'x', 'z', 'y0')
    # Face Y=box_dim
    create_face_emitters(box_dim, 'x', 'z', 'x', 'z', 'y1')
                
    return emitters

def genetic_algorithm_multi_target(target_positions, box, emitters, generations=50, pop_size=40):
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
    print("CYCLE 348: VOLUMETRIC 3D PRINTING (CUBE)")
    print("========================================")
    
    box_dim = 100.0
    box = AcousticSubstrate3D(width_mm=box_dim, height_mm=box_dim, depth_mm=box_dim, resolution_mm=2)
    
    # 6-sided array (384 emitters) for full 3D control
    emitters = create_phased_array_6_sides(box_dim=box_dim, num_emitters_per_side=8)
    print(f"Created 6-sided Phased Array: {len(emitters)} emitters.")
    
    # Define Cube Corners Targets (at 25mm offset from edges)
    offset = 25.0
    targets = [
        np.array([offset, offset, offset]),                        # (0,0,0)
        np.array([box_dim - offset, offset, offset]),              # (1,0,0)
        np.array([offset, box_dim - offset, offset]),              # (0,1,0)
        np.array([offset, offset, box_dim - offset]),              # (0,0,1)
        np.array([box_dim - offset, box_dim - offset, offset]),    # (1,1,0)
        np.array([box_dim - offset, offset, box_dim - offset]),    # (1,0,1)
        np.array([offset, box_dim - offset, box_dim - offset]),    # (0,1,1)
        np.array([box_dim - offset, box_dim - offset, box_dim - offset]) # (1,1,1)
    ]
    
    print(f"Targets: {len(targets)} points (Cube Formation).")
    
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
        tx, ty, tz = int(t[0]/box.resolution), int(t[1]/box.resolution), int(t[2]/box.resolution)
        p_val = potential[tz, ty, tx]
        ratio = p_val / p_max
        print(f"Corner {i}: Ratio {ratio:.4f}")
        results_data.append(ratio)
        
        if ratio > 0.2: success = False # Looser tolerance for 8 points + 3D
        
    output = {
        "cycle": 348,
        "shape": "cube_corners",
        "success": bool(success),
        "ratios": [float(r) for r in results_data]
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c348_volumetric_printing.json", "w") as f:
        json.dump(output, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Holographic 3D Cube Formed. Volumetric Matter Compilation achieved.")
    else:
        print("\n>> FAILURE: Could not stabilize 3D cube formation.")

if __name__ == "__main__":
    main()