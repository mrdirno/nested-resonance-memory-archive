
"""
Cycle 2346: Reality Compiler Verification
=========================================
Goal: Verify the end-to-end pipeline of Phase 43 (The Reality Compiler).
Process:
1. Generate a high-res Sphere OBJ.
2. Compile it using the `MatterCompiler`.
3. Visualize the intermediate Voxel Target (Gate 3.1).
4. Visualize the output Phase Map (Gate 3.2).

This script generates 'experiments/cycle2346_verification.png'.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Adjust path to find nrm_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.compiler import MatterCompiler

def create_sphere_obj(filename, radius=1.0, rings=16, sectors=16):
    """Generates a UV sphere OBJ file."""
    vertices = []
    faces = []
    
    # Generate vertices
    for r in range(rings + 1):
        theta = r * np.pi / rings
        for s in range(sectors + 1):
            phi = s * 2 * np.pi / sectors
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.cos(theta)
            z = radius * np.sin(theta) * np.sin(phi)
            vertices.append((x, y, z))
            
    # Generate faces
    for r in range(rings):
        for s in range(sectors):
            first = r * (sectors + 1) + s
            second = first + sectors + 1
            
            # Two triangles per sector
            faces.append((first + 1, second + 1, second))
            faces.append((first + 1, second, first))
            
    with open(filename, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            # OBJ indices are 1-based
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
            
    print(f"Generated Sphere: {len(vertices)} verts, {len(faces)} faces.")

def visualize_results(compiler, instruction_set, output_file):
    """Visualizes the Voxel Grid and the Phase Map."""
    
    # 1. Get Voxel Slice
    grid = compiler.voxelizer.grid
    mid_slice_idx = grid.shape[0] // 2
    voxel_slice = grid[mid_slice_idx, :, :]
    
    # 2. Get Phases
    # Reconstruct 8x8 grid from flat list
    phases = np.zeros((8, 8))
    for emitter in instruction_set['emitters']:
        # Position is [x, y, 0]. x, y are 0..1 normalized in default 8x8
        # Map back to index
        x_idx = int(emitter['position'][0] * 8)
        y_idx = int(emitter['position'][1] * 8)
        if 0 <= x_idx < 8 and 0 <= y_idx < 8:
            phases[x_idx, y_idx] = emitter['phase']
            
    # 3. Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot Voxel Target
    ax1 = axes[0]
    im1 = ax1.imshow(voxel_slice, cmap='Greys', origin='lower', vmin=0, vmax=1)
    ax1.set_title(f"Voxel Target (Slice z={mid_slice_idx})\nRes: {grid.shape[0]}x{grid.shape[1]}x{grid.shape[2]}")
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    
    # Plot Phase Solution
    ax2 = axes[1]
    im2 = ax2.imshow(phases, cmap='hsv', origin='lower', vmin=0, vmax=2*np.pi)
    ax2.set_title("Evolved Emitter Phases\n(8x8 Phased Array)")
    cbar = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Phase (Radians)")
    
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")

def main():
    print("--- Cycle 2346: Compiler Verification ---")
    
    obj_file = "data/temp_sphere.obj"
    
    # 1. Create Geometry
    if not os.path.exists("data"):
        os.makedirs("data")
    create_sphere_obj(obj_file)
    
    # 2. Run Compiler
    # Use 32 resolution for speed but enough detail for a sphere
    compiler = MatterCompiler(resolution=32)
    result = compiler.compile_object(obj_file, "AIR_STP")
    
    if result:
        print("Compilation Successful.")
        
        # 3. Visualize
        output_png = "experiments/cycle2346_verification.png"
        visualize_results(compiler, result, output_png)
        
    else:
        print("Compilation Failed.")
        
    # Cleanup
    if os.path.exists(obj_file):
        os.remove(obj_file)

if __name__ == "__main__":
    main()
