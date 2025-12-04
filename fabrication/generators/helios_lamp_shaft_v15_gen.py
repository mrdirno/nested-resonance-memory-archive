import numpy as np
import math
import sys
import struct
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V15: THE QUANTUM FIELD (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Particle Trajectory (Dissolving Helix).
# Math: Noise-modulated solidity.
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V15 SHAFT (Particle Trajectory): {output_path}")

    base_radius = 22.0
    core_radius = 7.5
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 15.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Probability Cloud intensity (Highest in middle)
        cloud_intensity = math.sin(z_norm * math.pi) 

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
                    # Standard Gyroid
                    gx = x_mm
                    gy = y_mm
                    gz = z_mm
                    
                    # Add noise to coordinates based on intensity
                    # This blurs the structure
                    noise = math.sin(x_mm*0.5)*math.cos(z_mm*0.8)
                    
                    gx += noise * cloud_intensity * 5.0
                    gy += noise * cloud_intensity * 5.0
                    
                    val = math.sin(gx * base_scale) * math.cos(gy * base_scale) + \
                          math.sin(gy * base_scale) * math.cos(gz * base_scale) + \
                          math.sin(gz * base_scale) * math.cos(gx * base_scale)
                    
                    if abs(val) < 0.45:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v15.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
