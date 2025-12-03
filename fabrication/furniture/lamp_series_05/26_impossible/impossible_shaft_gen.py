import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE IMPOSSIBLE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Necker Cube Column.
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating IMPOSSIBLE SHAFT: {output_path}")
    
    base_width = 30.0 # Square
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_width + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Twisted Square Beam
    twist_rate = math.pi / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        angle = z_norm * twist_rate
        
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
                    if abs(x_mm) < base_width/2 and abs(y_mm) < base_width/2:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Rotated Square
                rx = x_mm * math.cos(-angle) - y_mm * math.sin(-angle)
                ry = x_mm * math.sin(-angle) + y_mm * math.cos(-angle)
                
                # Cube Frame Logic (Anisotropic)
                
                box_size = 30.0
                frame_thick = 5.0
                
                # Anisotropy: Stretch Z periodic cuts
                z_period = 40.0 + z_norm * 40.0 # Accelerate period
                
                in_box = False
                if abs(rx) < box_size/2 and abs(ry) < box_size/2:
                    in_box = True
                    
                if in_box:
                    # Remove center of faces
                    cut_x = abs(rx) < (box_size/2 - frame_thick)
                    cut_y = abs(ry) < (box_size/2 - frame_thick)
                    
                    # Z periodic cuts
                    cut_z = (z_mm % z_period) > (z_period * 0.25) and (z_mm % z_period) < (z_period * 0.75)
                    
                    near_edge_x = abs(rx) > (box_size/2 - frame_thick)
                    near_edge_y = abs(ry) > (box_size/2 - frame_thick)
                    
                    if near_edge_x or near_edge_y:
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
    output_file = "impossible_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
