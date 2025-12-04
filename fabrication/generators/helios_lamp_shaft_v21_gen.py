import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V21: THE FLUID (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Liquid Column (Viscous Flow).
# Math: Metaballs / Blobby Noise.
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V21 SHAFT (Liquid Column): {output_path}")

    base_radius = 22.0
    core_radius = 7.5
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 20.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Flow: Vertical stretching
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - max_r
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - max_r
                
                dist = math.sqrt(x_mm**2 + y_mm**2)

                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                plug_check = lamp_lib.apply_shaft_plug_v2(z_mm, dist)
                if plug_check is True:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                if z_mm > (height - 2.0):
                    if dist <= base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                if dist <= base_radius:
                    # Liquid Flow
                    # Gyroid stretched heavily in Z
                    
                    val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                          math.sin(y_mm * base_scale) * math.cos(z_mm * base_scale * 0.3) + \
                          math.sin(z_mm * base_scale * 0.3) * math.cos(x_mm * base_scale)
                    
                    # Variable thickness (blobby)
                    # Add some noise to threshold
                    noise = math.sin(z_mm * 0.1) * 0.1
                    
                    if abs(val) < (0.5 + noise):
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v21.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
