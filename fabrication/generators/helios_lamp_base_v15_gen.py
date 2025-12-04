import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V15: THE QUANTUM FIELD (BASE)
# -----------------------------------------------------------------------------
# Concept: Wave Function (Ripple Interference).
# Math: Double-Slit Interference approximation.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V15 BASE (Wave Function): {output_path}")

    radius = diameter / 2.0
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Interference Sources
    s1 = (-20.0, 0.0)
    s2 = (20.0, 0.0)
    k = 2.0 * math.pi / 12.0 # Wavelength 12mm

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

                    # Interference Pattern
                    d1 = math.sqrt((x_mm - s1[0])**2 + (y_mm - s1[1])**2)
                    d2 = math.sqrt((x_mm - s2[0])**2 + (y_mm - s2[1])**2)
                    
                    # 3D Ripple
                    val = math.sin(d1 * k - z_mm*0.2) + math.sin(d2 * k - z_mm*0.2)
                    
                    # Add Gyroid texture to make it printable (avoid floating rings)
                    g_val = math.sin(x_mm*0.5)*math.cos(y_mm*0.5) + math.sin(z_mm*0.5)
                    
                    total = val * 0.7 + g_val * 0.3
                    
                    if abs(total) < 0.6:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v15.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
