import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE BRIDGE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Pylon (Cable Stay Tower).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating BRIDGE SHAFT: {output_path}")
    
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
        
        # Taper: Linearly decreases
        # But adds "Cable Stay" wings?
        
        current_radius = base_radius * (1.0 - 0.5 * z_norm)
        
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
                
                # Pylon Shape (Anisotropic)
                # X-Wing vs Y-Wing asymmetry
                
                in_wing = False
                wing_w = 4.0
                
                # Anisotropy: X-Wings are wider than Y-Wings
                if abs(x_mm) < (wing_w/2.0) and abs(y_mm) < current_radius: in_wing = True
                if abs(y_mm) < (wing_w/2.0) and abs(x_mm) < (current_radius * 0.6): in_wing = True # Shorter Y wings
                
                if in_wing:
                    # Cut holes in wings (Lightening holes - Stretched Z)
                    # Z pattern
                    
                    z_period = 30.0 # Stretched
                    if (z_mm % z_period) > (z_period * 0.6) and dist > 15.0:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    # Central column
                    if dist < (current_radius * 0.4):
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "bridge_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
