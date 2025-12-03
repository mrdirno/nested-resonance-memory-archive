import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE ARCHITECT (SHAFT)
# -----------------------------------------------------------------------------
# Logic: I-Beam (Structural Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating ARCHITECT SHAFT: {output_path}")
    
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
    
    # I-Beam Logic
    # Cross section is an I or H shape
    # Or cruciform (X beam)
    
    beam_w = 30.0
    flange_t = 5.0
    web_t = 6.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
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
                    if dist < (base_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Beam Profile
                # Cruciform
                in_beam = False
                
                # Vertical bar
                if abs(x_mm) < (web_t/2.0) and abs(y_mm) < (beam_w/2.0):
                    in_beam = True
                # Horizontal bar
                if abs(y_mm) < (web_t/2.0) and abs(x_mm) < (beam_w/2.0):
                    in_beam = True
                    
                # Flanges (Ends of bars)
                if abs(y_mm) > (beam_w/2.0 - flange_t) and abs(y_mm) < (beam_w/2.0) and abs(x_mm) < (beam_w/3.0):
                    in_beam = True # Top/Bottom caps
                    
                if abs(x_mm) > (beam_w/2.0 - flange_t) and abs(x_mm) < (beam_w/2.0) and abs(y_mm) < (beam_w/3.0):
                    in_beam = True # Left/Right caps
                    
                if in_beam:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "architect_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
