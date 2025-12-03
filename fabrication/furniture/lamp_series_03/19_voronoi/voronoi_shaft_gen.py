import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE VORONOI (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Organic Cell Stack, Library Integration.
# Logic: Stacked Cells (3D Voronoi Column).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating VORONOI SHAFT (v2.0): {output_path}")
    
    base_radius = 25.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # 3D Voronoi Logic
    # Scattered points along shaft
    import random
    random.seed(2025)
    
    num_cells = 50
    cells = []
    for _ in range(num_cells):
        r = random.uniform(10, base_radius)
        theta = random.uniform(0, 2*math.pi)
        z = random.uniform(0, height)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        cells.append((x,y,z))
        
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Taper
        current_radius = base_radius * (1.0 - 0.2 * z_norm)
            
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
                    if dist < (current_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Voronoi Foam (Organic v2.0 - Anisotropic)
                if dist <= current_radius:
                    d1 = 999.0
                    d2 = 999.0
                    
                    # Anisotropy: Stretch Z (Elongated Cells)
                    sz = 0.5
                    
                    # Opt: Check z distance first
                    for c in cells:
                        cx, cy, cz = c
                        if abs(z_mm - cz) > 50.0: continue # Increased range for stretch
                        
                        d_sq = (x_mm-cx)**2 + (y_mm-cy)**2 + ((z_mm-cz)*sz)**2
                        if d_sq < d1:
                            d2 = d1
                            d1 = d_sq
                        elif d_sq < d2:
                            d2 = d_sq
                            
                    d1 = math.sqrt(d1)
                    d2 = math.sqrt(d2)
                    
                    # Variable thickness
                    thickness = 2.0 + 2.0 * (1.0 - (z_mm/height)) # Thicker at bottom
                    
                    if (d2 - d1) < thickness: # Web
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "voronoi_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
