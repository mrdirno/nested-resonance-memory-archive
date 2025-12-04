import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V10: THE EVENT HORIZON (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Photon Sphere (Twisted Helix).
# Math: Helical Gyroid.
# -----------------------------------------------------------------------------

def rotate_coords(x, y, theta):
    c = math.cos(theta)
    s = math.sin(theta)
    rx = x * c - y * s
    ry = x * s + y * c
    return rx, ry

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V10 SHAFT (Photon Sphere): {output_path}")

    base_radius = 25.0
    waist_radius = 15.0 # Hourglass shape
    
    # Core
    core_radius = 7.0
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    twist_total = math.pi * 2.0 # Full 360 twist
    base_scale = 2.0 * math.pi / 12.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Profile: Hourglass (wider at ends)
        # Parabolic profile
        profile_r = waist_radius + (base_radius - waist_radius) * (2.0 * (z_norm - 0.5))**2
        
        current_radius = profile_r

        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - max_r
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - max_r
                
                dist = math.sqrt(x_mm**2 + y_mm**2)

                # Core Logic
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist <= current_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                if dist <= current_radius:
                    # Helical Twist
                    angle = z_norm * twist_total
                    rx, ry = rotate_coords(x_mm, y_mm, angle)
                    
                    lx = rx * base_scale
                    ly = ry * base_scale
                    lz = z_mm * base_scale
                    
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    is_solid = abs(val) < 0.45
                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v10.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
