import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V11: THE HYPER-DIMENSIONAL (BASE)
# -----------------------------------------------------------------------------
# Concept: Klein Manifold (Self-Intersecting Surface).
# Math: Parametric Klein Bottle logic adapted to Volumetric Grid.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V11 BASE (Klein Manifold): {output_path}")

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
    
    # Klein-ish Field Parameters
    # We simulate the "fold" by modulating density based on angle and radius
    # A true Klein bottle is a surface, we need a volume.
    # We'll use a "Twisted Torus" field.
    
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
                    hole_radius=rod_radius,
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

                # V2 Interface (Socket)
                socket_check = lamp_lib.apply_base_socket_v2(z_mm, dist, height)
                if socket_check is False:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                if dist <= radius:
                    # Klein Fold Logic
                    # Twist coordinate system 180 degrees as we go around the circle?
                    # Actually, let's use a Moebius strip logic for the lattice orientation
                    
                    angle = math.atan2(y_mm, x_mm)
                    
                    # 4D Rotation simulation
                    # w represents the 4th dimension, modulated by angle
                    w = math.sin(angle * 0.5) * 10.0
                    
                    lx = x_mm * base_scale
                    ly = y_mm * base_scale
                    lz = z_mm * base_scale
                    lw = w * base_scale
                    
                    # 4D Gyroid approximation: sum of cos(pairs)
                    # cos(x+w) + cos(y-w) + cos(z)
                    
                    val = math.cos(lx + lw) + math.cos(ly - lw) + math.cos(lz)
                    
                    threshold = 0.5 + (0.2 * (1.0 - (dist/radius)))
                    is_solid = abs(val) < threshold
                    
                    # Solid Rim/Core
                    if dist > (radius - 3.0): is_solid = True
                    if dist < 20.0: is_solid = True
                    if z_mm < 3.0: is_solid = True

                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v11.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
