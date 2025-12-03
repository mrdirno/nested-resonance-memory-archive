import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE TURING (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Stem Cell Column, Library Integration.
# Logic: Organic Growth Column (Cellular Texture).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating TURING SHAFT (v2.0): {output_path}")
    
    # Dimensions
    base_radius = 25.0
    
    # Core
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Pattern Params
    # Cell clusters
    # cos(x) * cos(y) * cos(z)
    scale = 2.0 * math.pi / 15.0 # Smaller cells
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Organic Taper
        current_radius = base_radius * (0.8 + 0.2*math.sin(z_norm * math.pi * 2))
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 QA Core Logic
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
                
                # Outer Shell
                if dist <= current_radius:
                    # Cellular Texture (v2.0)
                    # High frequency lattice
                    
                    val = math.cos(x_mm*scale) + math.cos(y_mm*scale) + math.cos(z_mm*scale)
                    
                    # Thicker walls
                    if val > -0.5:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "turing_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
