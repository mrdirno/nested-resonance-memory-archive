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
# HELIOS LAMP SERIES V13: THE NETWORK (BASE)
# -----------------------------------------------------------------------------
# Concept: Neural Root (Voronoi-like cellular structure).
# Math: Domain Warped Gyroid (Cellular approximation).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V13 BASE (Neural Root): {output_path}")

    radius = diameter / 2.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Cellular Params
    base_scale = 2.0 * math.pi / 18.0
    warp_scale = 2.0 * math.pi / 15.0
    warp_str = 3.0

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
                    hole_radius=7.5, # V2 Standard
                    radius=radius
                )
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue

                # V2 Socket Interface
                socket_check = lamp_lib.apply_base_socket_v2(z_mm, dist, height)
                if socket_check is False:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # Body Logic
                if dist <= radius:
                    # Solid Core
                    if dist < 20.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    if (z_mm < 2.0) or (z_mm > height - 2.0) or (dist > radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                    # Domain Warping for Cellular Look
                    wx = math.sin(x_mm * warp_scale) * warp_str
                    wy = math.cos(y_mm * warp_scale) * warp_str
                    wz = math.sin(z_mm * warp_scale) * warp_str
                    
                    gx = math.sin((x_mm+wx) * base_scale) * math.cos((y_mm+wy) * base_scale)
                    gy = math.sin((y_mm+wy) * base_scale) * math.cos((z_mm+wz) * base_scale)
                    gz = math.sin((z_mm+wz) * base_scale) * math.cos((x_mm+wx) * base_scale)
                    
                    val = gx + gy + gz
                    
                    # Thin walls for "Network" look
                    if abs(val) < 0.55:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v13.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
