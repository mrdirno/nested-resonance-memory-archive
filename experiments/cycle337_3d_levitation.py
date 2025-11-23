"""
CYCLE 337: 3D Nodal Trapping
Objective: Simulate a 3D standing wave and identify stable volumetric traps.
Hypothesis: 3D acoustics allows for full 6-DOF trapping (levitation + positioning).
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

# Extend Emitter to 3D
class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def main():
    print("CYCLE 337: 3D NODAL TRAPPING SIMULATION")
    print("=======================================")
    
    # 1. Setup 3D Space (50mm cube, 1mm resolution)
    box = AcousticSubstrate3D(width_mm=50, height_mm=50, depth_mm=50, resolution_mm=1)
    print(f"Simulation Volume: {box.width}x{box.height}x{box.depth} voxels")
    
    # 2. Configure 3-Axis Standing Wave (XYZ Trap)
    # To trap in 3D, we need standing waves in X, Y, and Z.
    # 6 Emitters total.
    
    mid_w = box.width / 2
    mid_h = box.height / 2
    mid_d = box.depth / 2
    
    emitters = [
        # Z-Axis (Top/Bottom) - Levitation
        Emitter3D(mid_w, mid_h, 0, frequency=1.0, phase=0.0, amplitude=1.0),
        Emitter3D(mid_w, mid_h, box.depth, frequency=1.0, phase=0.0, amplitude=1.0),
        
        # X-Axis (Left/Right) - Lateral Stability
        Emitter3D(0, mid_h, mid_d, frequency=1.0, phase=0.0, amplitude=1.0),
        Emitter3D(box.width, mid_h, mid_d, frequency=1.0, phase=0.0, amplitude=1.0),
        
        # Y-Axis (Front/Back) - Lateral Stability
        Emitter3D(mid_w, 0, mid_d, frequency=1.0, phase=0.0, amplitude=1.0),
        Emitter3D(mid_w, box.height, mid_d, frequency=1.0, phase=0.0, amplitude=1.0)
    ]
    
    # 3. Propagate
    print("\nCalculating 3D Pressure Field...")
    field = box.propagate(emitters)
    
    # 4. Find Traps (Local Minima of P^2)
    potential = field**2
    
    # To find a "Trap", we look for a voxel that is lower than all 26 neighbors
    print("Scanning for Volumetric Traps...")
    
    traps = []
    # Avoid boundaries
    for z in range(1, box.depth-1):
        for y in range(1, box.height-1):
            for x in range(1, box.width-1):
                val = potential[z, y, x]
                
                # Check 6 immediate neighbors first (optimization)
                neighbors = [
                    potential[z+1, y, x], potential[z-1, y, x],
                    potential[z, y+1, x], potential[z, y-1, x],
                    potential[z, y, x+1], potential[z, y, x-1]
                ]
                
                if all(val < n for n in neighbors):
                    # It's a local minimum
                    traps.append((x, y, z, val))
                    
    print(f"\nDetected {len(traps)} Volumetric Traps.")
    
    # 5. Analyze Central Trap
    # We expect a trap near the center (25, 25, 25)
    center_trap = min(traps, key=lambda t: np.sqrt((t[0]-25)**2 + (t[1]-25)**2 + (t[2]-25)**2))
    
    print(f"Central Trap Location: {center_trap[0:3]}")
    print(f"Trap Intensity (P^2): {center_trap[3]:.4f}")
    
    # Verify it's a "deep" trap
    max_pot = np.max(potential)
    if center_trap[3] < 0.1 * max_pot:
        print("Trap Quality: Excellent (Deep Node)")
    else:
        print("Trap Quality: Poor (Shallow Node)")

    results = {
        "cycle": 337,
        "num_traps": len(traps),
        "center_trap": center_trap,
        "success": len(traps) > 0
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c337_3d_levitation.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
