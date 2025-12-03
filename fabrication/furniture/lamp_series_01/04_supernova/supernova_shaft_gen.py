import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SUPERNOVA (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Shockwave Pulse, Library Integration.
# Logic: Cylinder with sharp, propagating ring pulses.
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating SUPERNOVA SHAFT (v2.0): {output_path}")
    
    # Dimensions
    base_radius = 15.0
    max_ripple = 8.0 # More aggressive
    
    # Core
    core_radius = 7.0 # 14mm ID
    core_wall_radius = 9.0
    
    max_r_bound = base_radius + max_ripple + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Ripple Params
    freq = 2.0 * math.pi / 20.0 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Ripple Function
        # Sharper ripples: sin^3 ?
        raw_wave = math.sin(z_mm * freq)
        ripple = raw_wave * abs(raw_wave) # Preserves sign but sharpens peaks
        
        current_radius = base_radius + (ripple * max_ripple)
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (base_radius - 1.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Outer Shell
                if dist <= current_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "supernova_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)