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
# HELIOS LAMP SERIES V17: THE SIMULATION (BASE)
# -----------------------------------------------------------------------------
# Concept: Render Failure (Low Poly / Glitch).
# Math: Coordinate Quantization + Axis Displacement.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V17 BASE (Render Failure): {output_path}")

    radius = diameter / 2.0
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 20.0
    
    # Glitch Params
    glitch_freq = 0.2
    glitch_amp = 5.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)

                # V4 Features
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist,
                    height=height,
                    hole_radius=7.5,
                    radius=radius
                )
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue

                # V2 Socket
                socket_check = lamp_lib.apply_base_socket_v2(z_mm, dist, height)
                if socket_check is False:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # Body
                if dist <= radius:
                    # Solid Core
                    if dist < 20.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    if (z_mm < 2.0) or (z_mm > height - 2.0) or (dist > radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                    # Glitch Logic: Axis-aligned shifts
                    # Shift X based on Y and Z
                    shift_x = 0
                    if math.sin(y_mm * glitch_freq) > 0.8:
                        shift_x = glitch_amp
                    
                    shift_y = 0
                    if math.cos(z_mm * glitch_freq) > 0.8:
                        shift_y = glitch_amp
                        
                    gx = x_mm + shift_x
                    gy = y_mm + shift_y
                    gz = z_mm
                    
                    # Low-Poly Look: Gyroid at standard resolution, but the shifts create "tearing"
                    val = math.sin(gx * base_scale) * math.cos(gy * base_scale) + \
                          math.sin(gy * base_scale) * math.cos(gz * base_scale) + \
                          math.sin(gz * base_scale) * math.cos(gx * base_scale)
                    
                    if abs(val) < 0.6:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v17.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
