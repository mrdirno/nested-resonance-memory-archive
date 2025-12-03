import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE LAG (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Lagged Segments (Sheared Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating LAG SHAFT: {output_path}")
    
    base_radius = 20.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 15.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Shearing center
        # Sudden shifts
        
        # Shift X based on Z "segments"
        segment = int(z_norm * 10.0)
        shift_x = 5.0 * (segment % 3 - 1)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                # Core is STRAIGHT (Physical wire needs straight path)
                dist_geo = math.sqrt(x_mm**2 + y_mm**2)
                
                # Outer shell is shifted
                dist_shift = math.sqrt((x_mm-shift_x)**2 + y_mm**2)
                
                # V4 QA Core
                if dist_geo < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist_geo < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist_geo < base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Lag Shell
                if dist_shift <= base_radius:
                    # Add texture
                    if (segment % 2) == 0:
                        # Ribbed
                        if math.sin(z_mm) > 0: grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Smooth
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lag_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
