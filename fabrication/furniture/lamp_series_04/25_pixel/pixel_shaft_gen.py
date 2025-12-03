import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE PIXEL (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Stacked Cubes (Minecraft Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating PIXEL SHAFT: {output_path}")
    
    base_radius = 20.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Cube Params (Anisotropic)
    # Tall rectangles
    cube_size_xy = 12.0
    cube_size_z = 24.0 
    
    import random
    random.seed(8080)
    
    # Generate stack of cubes along Z
    
    cubes = []
    num_layers = int(height / cube_size_z)
    for i in range(num_layers + 2):
        z = i * cube_size_z
        dx = random.uniform(-5, 5)
        dy = random.uniform(-5, 5)
        cubes.append((dx, dy, z))
        
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Find nearest cube layer
        layer_idx = int(z_mm / cube_size_z)
        if layer_idx >= len(cubes): layer_idx = len(cubes) - 1
        
        cx, cy, cz = cubes[layer_idx]
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 QA Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (base_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Cubes
                # Check if inside current cube
                if abs(x_mm - cx) < (cube_size_xy/2.0) and abs(y_mm - cy) < (cube_size_xy/2.0):
                    grid[x_idx,y_idx,z_idx] = True

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "pixel_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
