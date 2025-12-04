import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V20: THE FRACTAL (BASE)
# -----------------------------------------------------------------------------
# Concept: Menger Root (Recursive Cubic).
# Math: Multi-Scale Gyroid with Cubic Bias.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V20 BASE (Menger Root): {output_path}")

    radius = diameter / 2.0
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 30.0 # Large base blocks

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

                # V3 Structural Core
                core_check = lamp_lib.apply_base_structural_core(z_mm, dist, height)
                if core_check is True:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # Body
                if dist <= radius:
                    # Bed Adhesion
                    if (z_mm < 2.0) or (z_mm > height - 2.0) or (dist > radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                    # Fractal Logic
                    # cubic_bias pushes gyroid towards a cube shape
                    # val = sum(abs(sin(x)))
                    
                    s1 = base_scale
                    s2 = base_scale * 3.0
                    s3 = base_scale * 9.0
                    
                    # Menger-ish function:
                    # Union of cross shapes at different scales
                    # abs(x) < 1/3 or abs(y) < 1/3 ...
                    
                    # Let's stick to Gyroid summation but make it blocky
                    
                    g1 = math.sin(x_mm * s1) * math.cos(y_mm * s1) + \
                         math.sin(y_mm * s1) * math.cos(z_mm * s1) + \
                         math.sin(z_mm * s1) * math.cos(x_mm * s1)
                         
                    g2 = math.sin(x_mm * s2) * math.cos(y_mm * s2) + \
                         math.sin(y_mm * s2) * math.cos(z_mm * s2) + \
                         math.sin(z_mm * s2) * math.cos(x_mm * s2)
                         
                    g3 = math.sin(x_mm * s3) * math.cos(y_mm * s3) + \
                         math.sin(y_mm * s3) * math.cos(z_mm * s3) + \
                         math.sin(z_mm * s3) * math.cos(x_mm * s3)
                    
                    # Fractal Sum
                    # High frequency noise erodes the low frequency blocks
                    val = g1 + (0.5 * g2) + (0.25 * g3)
                    
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
    output_file = "base_v20.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
