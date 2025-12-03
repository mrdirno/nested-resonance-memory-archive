import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SINGULARITY (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Spaghettification Texture, Library Integration.
# Logic: Hyperboloid of One Sheet with extreme vertical stretching ribs.
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating SINGULARITY SHAFT (v2.0): {output_path}")
    
    # Dimensions
    waist_radius = 15.0
    base_radius = 35.0
    top_radius = 25.0
    
    # Core
    core_radius = 7.0 # 14mm Dia (V4 Std)
    core_wall_radius = 9.0
    
    max_radius = max(base_radius, top_radius) + 5.0
    step = height / resolution
    
    res_x = int(2 * max_radius / step) + 2
    res_y = int(2 * max_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Texture Scale (Spaghettification)
    # Many thin ribs
    rib_count = 24 
    rib_depth = 3.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Hyperboloid Profile (Aggressive waist)
        waist_z = 0.4
        
        if z_norm < waist_z:
            # Bottom section
            t = (waist_z - z_norm) / waist_z 
            current_base_radius = waist_radius + (base_radius - waist_radius) * (t**1.8)
        else:
            # Top section
            t = (z_norm - waist_z) / (1.0 - waist_z) 
            current_base_radius = waist_radius + (top_radius - waist_radius) * (t**2.2) 
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # V4 Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (waist_radius - 1.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Texture: Ribs that twist slightly and stretch
                # Twist increases near event horizon (waist)
                twist = z_norm * math.pi # 180 twist
                
                # Sharpen ribs for "spaghetti" look
                rib_raw = math.cos(rib_count * angle + twist)
                rib_mod = rib_raw * abs(rib_raw) # Square preserving sign for sharpness
                
                effective_radius = current_base_radius + (rib_mod * rib_depth)
                
                if dist <= effective_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, max_radius*2, max_radius*2)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "singularity_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
