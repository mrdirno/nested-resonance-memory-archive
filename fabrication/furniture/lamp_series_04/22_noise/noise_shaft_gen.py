import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE NOISE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Signal Loss (Distorted Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating NOISE SHAFT: {output_path}")
    
    base_radius = 20.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Noise Params
    scale = 2.0 * math.pi / 15.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Jitter center
        jitter_x = 2.0 * math.sin(z_mm * 0.5)
        jitter_y = 2.0 * math.cos(z_mm * 0.3)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                # Dist from geometric center
                dist_geo = math.sqrt(x_mm**2 + y_mm**2)
                
                # Dist from jitter center
                dist_jit = math.sqrt((x_mm-jitter_x)**2 + (y_mm-jitter_y)**2)
                
                # V4 QA Core (Geometric Center)
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
                
                # Noise Shell
                if dist_jit <= base_radius:
                    # Add noise to surface
                    n = math.sin(x_mm*scale) * math.sin(y_mm*scale) * math.sin(z_mm*scale)
                    
                    if n > -0.2:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "noise_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
