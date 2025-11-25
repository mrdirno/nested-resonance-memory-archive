
import numpy as np
import matplotlib.pyplot as plt
import torch
import sys
import os

# Add root to path to find nrm_core
# Assuming this script is in experiments/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
from nrm_core.helios.ga_gpu import genetic_algorithm_gpu
from nrm_core.helios.types import Emitter3D

def run_experiment():
    print("Initializing GPU Substrate...")
    box_dim = 100.0 # mm
    res = 1.0 # mm
    substrate = AcousticSubstrate3DGPU(width_mm=box_dim, height_mm=box_dim, depth_mm=box_dim, resolution_mm=res)
    
    print(f"Device: {substrate.device}")

    # Create Emitters (Simple 2-sided array for interference)
    emitters = []
    spacing = 10.0
    num = 8 # 8x8 array
    
    # Top and Bottom arrays (Z axis)
    center_offset = (num - 1) * spacing / 2.0
    center = box_dim / 2.0
    
    for i in range(num):
        for j in range(num):
            x = center - center_offset + i * spacing
            y = center - center_offset + j * spacing
            # Bottom firing up (z=0)
            emitters.append(Emitter3D(x, y, 0.0, 1.0, 1.0, 0.0)) 
            # Top firing down (z=box_dim)
            emitters.append(Emitter3D(x, y, box_dim, 1.0, 1.0, 0.0))

    # Target: Center
    target = np.array([center, center, center])
    targets = [target]
    
    print(f"Optimizing for target at {target} with {len(emitters)} emitters...")
    
    # Run GA
    # 20 generations is enough for a single point usually
    best_phases = genetic_algorithm_gpu(targets, substrate, emitters, generations=20, pop_size=40)
    
    print("Optimization Complete. Calculating Field...")
    
    # Apply phases to emitters
    for i, e in enumerate(emitters):
        e.phase = best_phases[i]
        
    # Propagate
    field = substrate.propagate(emitters)
    
    # Calculate Potential
    U = substrate.calculate_gorkov_potential(field)
    
    print(f"Field Shape: {U.shape}")
    
    # Slice at Z center
    # Z index
    z_idx = int(center / res)
    
    slice_u = U[z_idx, :, :] # (Height, Width)
    
    # Plot
    plt.figure(figsize=(10, 8))
    # Use extent to map indices to mm
    extent = [0, box_dim, 0, box_dim]
    plt.imshow(slice_u, origin='lower', extent=extent, cmap='viridis_r') # _r for reversed (traps are dark/low)
    plt.colorbar(label='Gorkov Potential (Arbitrary Units)')
    plt.scatter([center], [center], c='red', marker='x', label='Target')
    plt.title(f"Acoustic Trap at Z={center}mm (GPU Accelerated)")
    plt.xlabel("X (mm)")
    plt.ylabel("Y (mm)")
    plt.legend()
    
    output_path = os.path.join(os.path.dirname(__file__), 'cycle564_trap.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")
    
    # Check if trap is stable (local minimum)
    # Center value should be lower than surroundings
    center_val = slice_u[int(center/res), int(center/res)]
    print(f"Potential at target: {center_val}")
    
    # Simple check: is it the minimum in the slice?
    min_val = np.min(slice_u)
    print(f"Min potential in slice: {min_val}")
    
    if abs(center_val - min_val) < 1e-6: # Floating point tolerance
        print("SUCCESS: Target is the global minimum in the slice.")
    else:
        print("WARNING: Target might not be the global minimum.")

if __name__ == "__main__":
    run_experiment()
