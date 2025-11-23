"""
CYCLE 349: The Dynamic Engine (4D Printing)
Objective: Demonstrate "Active Object Manipulation" (Telekinesis of Structure) by rotating the 8-point cubic lattice in 3D space.
Hypothesis: By interpolating between phase solutions for rotated target sets, we can smoothly animate the matter without losing confinement.
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
    emitters = []
    def create_face_emitters(fixed_coord, axis1, axis2, val1, val2, orientation):
        center_offset1 = (num_emitters_per_side - 1) * emitter_spacing / 2.0
        center_offset2 = (num_emitters_per_side - 1) * emitter_spacing / 2.0
        box_center = box_dim / 2.0
        for i in range(num_emitters_per_side):
            for j in range(num_emitters_per_side):
                coord1 = box_center - center_offset1 + i * emitter_spacing
                coord2 = box_center - center_offset2 + j * emitter_spacing
                if orientation == 'z0': emitters.append(Emitter3D(coord1, coord2, fixed_coord, 1.0, 0.0))
                elif orientation == 'z1': emitters.append(Emitter3D(coord1, coord2, fixed_coord, 1.0, 0.0))
                elif orientation == 'x0': emitters.append(Emitter3D(fixed_coord, coord1, coord2, 1.0, 0.0))
                elif orientation == 'x1': emitters.append(Emitter3D(fixed_coord, coord1, coord2, 1.0, 0.0))
                elif orientation == 'y0': emitters.append(Emitter3D(coord1, fixed_coord, coord2, 1.0, 0.0))
                elif orientation == 'y1': emitters.append(Emitter3D(coord1, fixed_coord, coord2, 1.0, 0.0))
    create_face_emitters(0.0, 'x', 'y', 'x', 'y', 'z0')
    create_face_emitters(box_dim, 'x', 'y', 'x', 'y', 'z1')
    create_face_emitters(0.0, 'y', 'z', 'y', 'z', 'x0')
    create_face_emitters(box_dim, 'y', 'z', 'y', 'z', 'x1')
    create_face_emitters(0.0, 'x', 'z', 'x', 'z', 'y0')
    create_face_emitters(box_dim, 'x', 'z', 'x', 'z', 'y1')
    return emitters

def genetic_algorithm_multi_target(target_positions, box, emitters, generations=30, pop_size=30, initial_guess=None):
    """
    GA optimization. Can be seeded with an 'initial_guess' (e.g. previous frame solution) for continuity.
    """
    num_emitters = len(emitters)
    
    if initial_guess is not None:
        # Seed population with slight variations of the guess
        population = []
        for _ in range(pop_size):
            # Perturb phases slightly (Gaussian noise)
            noise = np.random.normal(0, 0.5, num_emitters)
            ind = (initial_guess + noise) % (2 * np.pi)
            population.append(ind)
    else:
        population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    best_genes = None
    best_score = -9999.0
    
    for gen in range(generations):
        scores = []
        for individual in population:
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
                    current_score += (p_max - p_val)
                else:
                    current_score -= 50.0
            scores.append((current_score, individual))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        if scores[0][0] > best_score:
            best_score = scores[0][0]
            best_genes = scores[0][1]
            
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

def rotate_points(points, angle_deg, axis='z', center=np.array([50.0, 50.0, 50.0])):
    """
    Rotates a set of points around a center.
    """
    angle_rad = np.radians(angle_deg)
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    
    rotated_points = []
    for p in points:
        # Translate to origin
        v = p - center
        
        if axis == 'z':
            # Rotation matrix around Z
            x_new = v[0] * c - v[1] * s
            y_new = v[0] * s + v[1] * c
            z_new = v[2]
        elif axis == 'y':
            x_new = v[0] * c + v[2] * s
            y_new = v[1]
            z_new = -v[0] * s + v[2] * c
        # ... (add other axes if needed)
        
        new_v = np.array([x_new, y_new, z_new])
        rotated_points.append(new_v + center)
        
    return rotated_points

def main():
    print("CYCLE 349: THE DYNAMIC ENGINE (4D PRINTING)")
    print("===========================================")
    
    box_dim = 100.0
    box = AcousticSubstrate3D(width_mm=box_dim, height_mm=box_dim, depth_mm=box_dim, resolution_mm=2)
    emitters = create_phased_array_6_sides(box_dim=box_dim, num_emitters_per_side=8)
    
    # Define Initial Cube (Frame 0)
    offset = 25.0
    initial_targets = [
        np.array([offset, offset, offset]),
        np.array([box_dim - offset, offset, offset]),
        np.array([offset, box_dim - offset, offset]),
        np.array([offset, offset, box_dim - offset]),
        np.array([box_dim - offset, box_dim - offset, offset]),
        np.array([box_dim - offset, offset, box_dim - offset]),
        np.array([offset, box_dim - offset, box_dim - offset]),
        np.array([box_dim - offset, box_dim - offset, box_dim - offset])
    ]
    
    print("Generating Frame 0 (0 degrees)...")
    phases_0 = genetic_algorithm_multi_target(initial_targets, box, emitters)
    
    # Generate Frame 1 (45 degrees rotation)
    print("Generating Frame 1 (45 degrees Z-Rotation)...")
    rotated_targets = rotate_points(initial_targets, 45.0, axis='z')
    
    # Use phases_0 as seed for faster convergence and smoothness
    phases_1 = genetic_algorithm_multi_target(rotated_targets, box, emitters, initial_guess=phases_0)
    
    # Verify Frame 1 Stability
    print("\nVerifying Frame 1 Stability:")
    for i, e in enumerate(emitters): e.phase = phases_1[i]
    field = box.propagate(emitters)
    potential = field**2
    p_max = np.max(potential)
    
    success = True
    ratios = []
    for i, t in enumerate(rotated_targets):
        tx, ty, tz = int(t[0]/box.resolution), int(t[1]/box.resolution), int(t[2]/box.resolution)
        p_val = potential[tz, ty, tx]
        ratio = p_val / p_max
        ratios.append(ratio)
        print(f"Corner {i}: Ratio {ratio:.4f}")
        if ratio > 0.2: success = False
        
    # Calculate "Smoothness" (Correlation between phases)
    # We want phases to change smoothly, not jump randomly.
    # Phase difference:
    phase_diff = np.abs(phases_1 - phases_0)
    phase_diff = np.minimum(phase_diff, 2*np.pi - phase_diff) # Shortest path on circle
    mean_diff = np.mean(phase_diff)
    print(f"\nMean Phase Shift: {mean_diff:.4f} radians")
    
    output = {
        "cycle": 349,
        "action": "rotation_45_deg",
        "success": bool(success),
        "mean_phase_shift": float(mean_diff),
        "ratios": [float(r) for r in ratios]
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c349_dynamic_engine.json", "w") as f:
        json.dump(output, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: 4D Rotation Achieved. The object moved coherently.")
    else:
        print("\n>> FAILURE: Object lost coherence during rotation.")

if __name__ == "__main__":
    main()