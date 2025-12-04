import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V16: THE TESSERACT (BASE)
# -----------------------------------------------------------------------------
# Concept: Hypercube Shadow.
# Math: Schwarz P-Surface (Cubic) with 4D Projection bias.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V16 BASE (Hypercube Shadow): {output_path}")

    radius = diameter / 2.0
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Cubic Params
    base_scale = 2.0 * math.pi / 20.0

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

                    # 4D Cubic Projection
                    # w = distance from center (Hyper-spherical slicing)
                    w = dist * 0.1
                    
                    # Schwarz P (Cubic)
                    # cos(x) + cos(y) + cos(z) + cos(w) = 0
                    
                    lx = x_mm * base_scale
                    ly = y_mm * base_scale
                    lz = z_mm * base_scale
                    lw = w * base_scale
                    
                    val = math.cos(lx) + math.cos(ly) + math.cos(lz) + math.cos(lw)
                    
                    # Threshold for "open" lattice
                    if abs(val) < 0.7:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v16.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
