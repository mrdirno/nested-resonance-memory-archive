import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE TIME CRYSTAL (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: 4D Hyper-Lattice, Library Integration.
# Logic: Periodic crystal structure (Repeating 4D pattern).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating TIME SHAFT (v2.0): {output_path}")
    
    # Dimensions
    base_radius = 20.0
    
    # Core
    core_radius = 7.0 # 14mm ID (V4 Std)
    core_wall_radius = 9.0
    
    max_radius = base_radius + 5.0
    step = height / resolution
    
    res_x = int(2 * max_radius / step) + 2
    res_y = int(2 * max_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Lattice Params (v2.0: Complex periodic)
    freq = 2.0 * math.pi / 20.0 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_radius
                
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
                
                # 4D Lattice Projection
                # cos(x) + cos(y) + cos(z) + cos(w)
                # map w to z or radius?
                # let's map w to (x+y+z)
                
                val = math.cos(x_mm * freq) + math.cos(y_mm * freq) + math.cos(z_mm * freq)
                
                # Add 4th dimension interference
                w = (x_mm + y_mm + z_mm) * 0.5
                val += math.cos(w * freq)
                
                # Lattice Structure
                if dist <= base_radius:
                    if val > 1.5: # Nodes
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_radius, 2*max_radius)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "time_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)