import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE FIRE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Rising Smoke (Twisting/Dissipating).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating FIRE SHAFT: {output_path}")
    
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
    
    # Smoke Params
    twist_rate = 3.0 * math.pi 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Taper: Thinning out
        current_radius = base_radius * (1.0 - 0.4 * z_norm)
        
        angle_offset = z_norm * twist_rate
        
        # Drift
        drift_x = 5.0 * math.sin(z_norm * math.pi)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                # Origin distance
                dist_geo = math.sqrt(x_mm**2 + y_mm**2)
                
                # Drifted/Twisted coords
                xd = x_mm - drift_x
                yd = y_mm
                
                # Rotate
                xr = xd * math.cos(angle_offset) - yd * math.sin(angle_offset)
                yr = xd * math.sin(angle_offset) + yd * math.cos(angle_offset)
                
                dist_smoke = math.sqrt(xr**2 + yr**2)
                
                # V4 QA Core
                if dist_geo < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist_geo < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist_geo < (base_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Smoke Shape
                # Lobes
                angle_smoke = math.atan2(yr, xr)
                r_blob = current_radius + 5.0 * math.sin(3.0 * angle_smoke + z_mm*0.1)
                
                if dist_smoke <= r_blob:
                    # Dissipation at top?
                    if z_norm > 0.8:
                        # Noise cuts
                        noise = math.sin(x_mm*0.5)*math.cos(y_mm*0.5)*math.sin(z_mm*0.5)
                        if noise > (z_norm - 0.5): # More holes higher up
                            grid[x_idx,y_idx,z_idx] = False
                        else:
                            grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fire_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
