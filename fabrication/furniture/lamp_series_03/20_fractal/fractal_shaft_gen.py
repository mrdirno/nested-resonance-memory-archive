import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE FRACTAL (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Menger Tower (High Iteration), Library Integration.
# Logic: Infinite Column (Menger Sponge Tower).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating FRACTAL SHAFT (v2.0): {output_path}")
    
    base_width = 45.0 # Square column
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_width + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Menger Logic (v2.0: 3 Iterations)
    # Sizes
    s1 = 15.0
    s2 = 5.0
    s3 = 1.66
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                # Square boundary
                if abs(x_mm) > (base_width/2) or abs(y_mm) > (base_width/2):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
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
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Menger Sponge (Anisotropic)
                # Stretch Z scale
                
                px = abs(x_mm)
                py = abs(y_mm)
                pz = z_mm * 0.5 # Z-Stretch (makes blocks taller)
                
                is_cut = False
                
                # Iteration 1
                c1 = 0
                if (px % (s1*3)) > s1 and (px % (s1*3)) < (s1*2): c1 += 1
                if (py % (s1*3)) > s1 and (py % (s1*3)) < (s1*2): c1 += 1
                if (pz % (s1*3)) > s1 and (pz % (s1*3)) < (s1*2): c1 += 1
                if c1 >= 2: is_cut = True
                
                # Iteration 2
                if not is_cut:
                    c2 = 0
                    if (px % (s2*3)) > s2 and (px % (s2*3)) < (s2*2): c2 += 1
                    if (py % (s2*3)) > s2 and (py % (s2*3)) < (s2*2): c2 += 1
                    if (pz % (s2*3)) > s2 and (pz % (s2*3)) < (s2*2): c2 += 1
                    if c2 >= 2: is_cut = True
                    
                # Iteration 3 (Only near surface?)
                if not is_cut:
                    c3 = 0
                    if (px % (s3*3)) > s3 and (px % (s3*3)) < (s3*2): c3 += 1
                    if (py % (s3*3)) > s3 and (py % (s3*3)) < (s3*2): c3 += 1
                    if (pz % (s3*3)) > s3 and (pz % (s3*3)) < (s3*2): c3 += 1
                    if c3 >= 2: is_cut = True
                
                if is_cut:
                    grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = True

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fractal_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
