import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V10: THE EVENT HORIZON (BASE)
# -----------------------------------------------------------------------------
# Concept: Accretion Disk (Swirling Spiral Lattice).
# Math: Domain Warped Gyroid (Rotational Bias).
# -----------------------------------------------------------------------------

def rotate_coords(x, y, theta):
    c = math.cos(theta)
    s = math.sin(theta)
    rx = x * c - y * s
    ry = x * s + y * c
    return rx, ry

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V10 BASE (Accretion Disk): {output_path}")

    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0
    foot_radius = 10.0
    foot_depth = 3.0
    foot_offset = 15.0
    channel_height = 8.0
    channel_width = 8.0

    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Warping Params
    twist_strength = 0.10 # Reduced from 0.15 to prevent tearing
    base_scale = 2.0 * math.pi / 15.0

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
                    hole_radius=7.5, # QA V2
                    channel_height=channel_height,
                    channel_width=channel_width,
                    foot_depth=foot_depth,
                    foot_radius=foot_radius,
                    foot_offset=foot_offset,
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

                # Body Logic
                if dist <= radius:
                    # 1. Accretion Warping
                    # Twist angle increases with radius (dragging outer rim)
                    angle = dist * twist_strength
                    rx, ry = rotate_coords(x_mm, y_mm, angle)
                    
                    # 2. Gyroid Evaluation
                    lx = rx * base_scale
                    ly = ry * base_scale
                    lz = z_mm * base_scale
                    
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    # 3. Density Gradient (Denser near event horizon/center)
                    # Thicker walls to ensure connectivity
                    threshold = 0.5 + (0.3 * (1.0 - (dist/radius))) 
                    
                    is_solid = abs(val) < threshold
                    
                    # Solid Rim
                    if dist > (radius - 4.0): is_solid = True # Thicker rim
                    if z_mm < 3.0: is_solid = True # Bed adhesion

                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Export
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v10.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)