import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE EARTH (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Stalactite (Dripstone Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating EARTH SHAFT: {output_path}")
    
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
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Taper: Irregular
        # radius = base * (1 - noise)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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
                
                # Stalactite Shape
                # Drips = downward flow
                # sin(N*theta) modulated by exp(-z) ?
                
                # Base cylinder
                r_base = base_radius * 0.6
                
                # Drips
                drip_val = math.sin(5.0 * angle) * math.sin(x_mm*0.1)
                drip_ext = 8.0 * (math.sin(z_mm*0.1 + drip_val) + 1.0)
                
                r_surf = r_base + drip_ext
                
                if dist <= r_surf:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "earth_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
