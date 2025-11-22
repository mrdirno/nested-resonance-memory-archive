"""
CYCLE 341: Swarm Levitation (Acoustic Chemistry)
Objective: Trap two particles simultaneously and manipulate their relative distance (Bond Length).
Hypothesis: By superimposing the phase solutions for two targets, we can create a composite field with two distinct potential wells.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def calculate_phases_for_multi_target(targets, emitters, k):
    """
    Holographic Superposition for Multiple Traps.
    For N targets, the complex field at emitter i is the sum of the required fields for each target.
    Ideally, we want destructive interference at ALL targets.
    
    Simple approach:
    We calculate the phase required for Target A.
    We calculate the phase required for Target B.
    We vector-sum the complex amplitudes? 
    Or we assume time-multiplexing (persistence of vision/inertia).
    
    Let's try Time-Multiplexing first (Rapid switching).
    It's robust and simpler.
    But for "Acoustic Chemistry", simultaneous is better.
    
    Let's try "Weighted Superposition".
    Complex E_i = Sum_j ( exp(i * phi_ij) )
    Phase_i = arg(E_i)
    """
    new_phases = []
    for e in emitters:
        # Sum complex phasors
        complex_sum = 0j
        for target_pos in targets:
            dist = np.sqrt((e.x - target_pos[0])**2 + (e.y - target_pos[1])**2 + (e.z - target_pos[2])**2)
            # Phase for Node at target: -k*d
            phi = -(k * dist)
            complex_sum += np.exp(1j * phi)
            
        # Resultant phase
        if abs(complex_sum) > 0:
            new_phases.append(np.angle(complex_sum))
        else:
            new_phases.append(0.0)
            
    return new_phases

def find_local_minima(box, emitters):
    """Finds all potential wells."""
    field = box.propagate(emitters)
    potential = field**2
    
    traps = []
    # Sparse search for speed
    step = 2
    for z in range(2, box.depth-2, step):
        for y in range(2, box.height-2, step):
            for x in range(2, box.width-2, step):
                val = potential[z,y,x]
                # Check immediate neighbors
                is_min = True
                neighbors = [
                    potential[z+1,y,x], potential[z-1,y,x],
                    potential[z,y+1,x], potential[z,y-1,x],
                    potential[z,y,x+1], potential[z,y,x-1]
                ]
                if any(val >= n for n in neighbors):
                    is_min = False
                
                if is_min and val < 0.1: # Only deep traps
                    traps.append(np.array([float(x), float(y), float(z)]))
    return traps, potential

def main():
    print("CYCLE 341: SWARM LEVITATION (ACOUSTIC CHEMISTRY)")
    print("==============================================")
    
    # 1. Setup
    box = AcousticSubstrate3D(width_mm=60, height_mm=60, depth_mm=60, resolution_mm=1)
    mid_w, mid_h, mid_d = 30.0, 30.0, 30.0
    
    # 6-Axis Emitter Array
    emitters = [
        Emitter3D(mid_w, mid_h, 0, 1.0, 0.0), Emitter3D(mid_w, mid_h, 60, 1.0, 0.0),
        Emitter3D(0, mid_h, mid_d, 1.0, 0.0), Emitter3D(60, mid_h, mid_d, 1.0, 0.0),
        Emitter3D(mid_w, 0, mid_d, 1.0, 0.0), Emitter3D(mid_w, 60, mid_d, 1.0, 0.0)
    ]
    
    freq_hz = 40000
    v = 343.0
    grid_k = (2 * np.pi * freq_hz / v) * 0.001
    
    # 2. Define Molecule (Two Atoms)
    # Initial state: Bond Length 10mm
    atom_a = np.array([25.0, 30.0, 30.0])
    atom_b = np.array([35.0, 30.0, 30.0])
    
    print(f"Atom A: {atom_a}, Atom B: {atom_b}")
    print(f"Initial Bond Length: {np.linalg.norm(atom_a - atom_b)} mm")
    
    # 3. Superposition Calculation
    phases = calculate_phases_for_multi_target([atom_a, atom_b], emitters, grid_k)
    for i, e in enumerate(emitters):
        e.phase = phases[i]
        
    # 4. Verify Traps
    print("\nSimulating Field...")
    traps, potential = find_local_minima(box, emitters)
    
    print(f"Detected {len(traps)} total deep traps.")
    
    # Find traps closest to A and B
    trap_a = min(traps, key=lambda t: np.linalg.norm(t - atom_a)) if traps else None
    trap_b = min(traps, key=lambda t: np.linalg.norm(t - atom_b)) if traps else None
    
    success = False
    dist_a = float('inf')
    dist_b = float('inf')
    
    if trap_a is not None and trap_b is not None:
        dist_a = np.linalg.norm(trap_a - atom_a)
        dist_b = np.linalg.norm(trap_b - atom_b)
        
        print(f"Trap A found at {trap_a} (Error: {dist_a:.2f} mm)")
        print(f"Trap B found at {trap_b} (Error: {dist_b:.2f} mm)")
        
        # Check if they are distinct
        if np.linalg.norm(trap_a - trap_b) > 1.0:
            success = True
            print(">> SUCCESS: Distinct traps formed for both atoms.")
        else:
            print(">> FAILURE: Traps merged into one.")
            
    # 5. Bonding Animation (Stretch)
    # Move them apart to 20mm
    print("\n--- Stretching Bond ---")
    target_bond = 20.0
    # New positions
    new_a = np.array([20.0, 30.0, 30.0])
    new_b = np.array([40.0, 30.0, 30.0])
    
    phases = calculate_phases_for_multi_target([new_a, new_b], emitters, grid_k)
    for i, e in enumerate(emitters):
        e.phase = phases[i]
        
    traps, _ = find_local_minima(box, emitters)
    trap_a_new = min(traps, key=lambda t: np.linalg.norm(t - new_a)) if traps else None
    trap_b_new = min(traps, key=lambda t: np.linalg.norm(t - new_b)) if traps else None
    
    bond_success = False
    if trap_a_new is not None and trap_b_new is not None:
        actual_bond = np.linalg.norm(trap_a_new - trap_b_new)
        print(f"Target Bond: {target_bond} mm | Actual Bond: {actual_bond:.2f} mm")
        if abs(actual_bond - target_bond) < 2.0:
            bond_success = True
            print(">> SUCCESS: Bond stretched successfully.")
    
    results = {
        "cycle": 341,
        "initial_bond": 10.0,
        "stretched_bond": float(actual_bond) if bond_success else 0.0,
        "success": success and bond_success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c341_swarm_levitation.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
