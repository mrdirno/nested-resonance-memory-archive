"""
CYCLE 338: The Active Matter Loop (Telekinesis)
Objective: Dynamically move a trapped particle by continuously updating emitter phases.
Hypothesis: Smooth phase transitions will translate the trapping node without losing confinement depth (Dropping the particle).
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

# Extend Emitter to 3D (Redefined here for clarity, matches C337)
class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def calculate_phases_for_target(target_pos, emitters, k):
    """
    Inverse Kinematics for Acoustic Trapping.
    To create a trap at target_pos (x,y,z), the phase of each emitter must align 
    such that they destructively interfere (node) or constructively interfere (antinode) 
    depending on the trap type.
    
    Simple Logic: To make a node at T, we want phases to cancel.
    Standard levitation usually employs a standing wave. 
    Phase_i = k * distance(E_i, T) + pi (for destructive) or 0 (for constructive)
    
    Let's try to maintain a Standing Wave Node.
    Ideally, opposed emitters should have phases that result in cancellation at T.
    If dist1 and dist2 are distances from opposed emitters:
    k*d1 + phi1 = k*d2 + phi2 + pi  (Destructive interference condition)
    
    Simplified for this experiment: We act as if we are "focusing" at the target, 
    but we know from C335 that focusing creates an Antinode (Repulsor).
    Traps form *adjacent* to the focus. 
    So if we move the Focus, the Trap moves with it.
    """
    new_phases = []
    for e in emitters:
        dist = np.sqrt((e.x - target_pos[0])**2 + (e.y - target_pos[1])**2 + (e.z - target_pos[2])**2)
        # Phase to focus at target: -k*d
        # This creates a pressure MAX at target (Antinode).
        # The Node will be lambda/4 away.
        # If we move the "Focus Point", the "Node" moves rigidly with it.
        phi = -(k * dist) % (2 * np.pi)
        new_phases.append(phi)
    return new_phases

def main():
    print("CYCLE 338: ACTIVE MATTER LOOP (TELEKINESIS)")
    print("===========================================")
    
    # 1. Setup 3D Space (Small volume for speed)
    # 60x60x60 mm, 1mm resolution
    box = AcousticSubstrate3D(width_mm=60, height_mm=60, depth_mm=60, resolution_mm=1)
    
    mid_w = box.width / 2
    mid_h = box.height / 2
    mid_d = box.depth / 2
    
    # 2. Emitters (6-Axis)
    # Positions in Grid Coordinates (mm)
    emitters = [
        Emitter3D(mid_w, mid_h, 0, 1.0, 0.0), Emitter3D(mid_w, mid_h, box.depth, 1.0, 0.0), # Z
        Emitter3D(0, mid_h, mid_d, 1.0, 0.0), Emitter3D(box.width, mid_h, mid_d, 1.0, 0.0), # X
        Emitter3D(mid_w, 0, mid_d, 1.0, 0.0), Emitter3D(mid_w, box.height, mid_d, 1.0, 0.0) # Y
    ]
    
    # Physics Constants
    freq_hz = 40000 # 40kHz
    wave_speed = 343.0 # m/s
    # k in grid units (1 unit = 1 mm = 0.001 m)
    # real_k = 2*pi*f/v (radians per meter)
    # grid_k = real_k * 0.001 (radians per mm)
    real_k = 2 * np.pi * freq_hz / wave_speed
    grid_k = real_k * 0.001
    
    print(f"Wavelength: {wave_speed/freq_hz*1000:.2f} mm")
    
    # 3. Trajectory Definition
    # Move "Focus" from (30,30,30) to (40,30,30) over 10 steps.
    # Note: Particle will trap at a Node near this focus.
    start_pos = np.array([30.0, 30.0, 30.0])
    end_pos = np.array([40.0, 30.0, 30.0])
    steps = 10
    
    print(f"\nTrajectory: {start_pos} -> {end_pos} ({steps} steps)")
    
    trajectory_log = []
    
    for i in range(steps + 1):
        t = i / steps
        current_target = start_pos + t * (end_pos - start_pos)
        
        # A. Calculate Phases (The Cognitive Act)
        phases = calculate_phases_for_target(current_target, emitters, grid_k)
        
        # B. Update Emitters (The Physical Act)
        for j, e in enumerate(emitters):
            e.phase = phases[j]
            
        # C. Simulate Field (The Reality)
        field = box.propagate(emitters)
        potential = field**2
        
        # D. Find Trap Center (Observation)
        # We verify if a deep node exists near the target focus
        # Search neighborhood of current_target
        tx, ty, tz = int(current_target[0]), int(current_target[1]), int(current_target[2])
        
        # Local search for min
        search_radius = 5
        min_val = float('inf')
        min_loc = None
        
        for z in range(max(0, tz-search_radius), min(box.depth, tz+search_radius)):
            for y in range(max(0, ty-search_radius), min(box.height, ty+search_radius)):
                for x in range(max(0, tx-search_radius), min(box.width, tx+search_radius)):
                    val = potential[z,y,x]
                    if val < min_val:
                        min_val = val
                        min_loc = (x,y,z)
        
        # Log
        offset = np.array(min_loc) - current_target
        dist_offset = np.linalg.norm(offset)
        
        log_entry = {
            "step": i,
            "target": current_target.tolist(),
            "trap_loc": min_loc,
            "trap_depth": float(min_val),
            "offset_dist": float(dist_offset)
        }
        trajectory_log.append(log_entry)
        
        print(f"Step {i}: Target={current_target.astype(int)} | Trap={min_loc} | Depth={min_val:.4f} | Offset={dist_offset:.2f}")

    # 4. Validation
    # Success if trap depth stays low (confinement maintained) and trap moves with target
    # Offset should be roughly constant (the node-antinode distance)
    
    max_depth = max(entry['trap_depth'] for entry in trajectory_log)
    final_pos = trajectory_log[-1]['trap_loc']
    initial_pos = trajectory_log[0]['trap_loc']
    
    displacement = np.linalg.norm(np.array(final_pos) - np.array(initial_pos))
    
    print(f"\nTotal Displacement: {displacement:.2f} mm")
    print(f"Max Potential (Leakage): {max_depth:.4f}")
    
    success = displacement > 5.0 and max_depth < 0.1 # Arbitrary threshold for "low" potential
    
    results = {
        "cycle": 338,
        "trajectory": trajectory_log,
        "displacement": displacement,
        "max_leakage": max_depth,
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c338_active_matter_loop.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Particle moved via phase-shifting. Telekinesis verified.")
    else:
        print("\n>> FAILURE: Particle did not move or trap was lost.")

if __name__ == "__main__":
    main()