import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V30: THE AETHER (BASE)
# -----------------------------------------------------------------------------
# Concept: Zero Point (Triangular Flow).
# Math: Triangular Wave Gyroid + Vortex Warp.
# -----------------------------------------------------------------------------

def tri_wave(t):
    # Approximation of triangle wave using arcsin
    # Range [-1.57, 1.57] approx
    return math.asin(math.sin(t))

def tri_gyroid(x, y, z, scale):
    # Standard Gyroid equation but with Triangle Waves instead of Sine
    # This creates sharper, more angular "crystals" that still flow
    
    sx = tri_wave(x * scale)
    cy = tri_wave(y * scale + math.pi/2) # Cosine equivalent
    sy = tri_wave(y * scale)
    cz = tri_wave(z * scale + math.pi/2)
    sz = tri_wave(z * scale)
    cx = tri_wave(x * scale + math.pi/2)
    
    return sx*cy + sy*cz + sz*cx

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V30 BASE (Zero Point): {output_path}")

    radius = diameter / 2.0
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 25.0

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

                # V2 Socket Interface
                socket_check = lamp_lib.apply_base_socket_v2(z_mm, dist, height)
                if socket_check is False:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # V3 Structural Core (Cup)
                # Ensure this is skeletal, not a block
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

                    # Vortex Warp
                    angle = math.atan2(y_mm, x_mm)
                    twist = dist * 0.05 # Gentle twist
                    
                    c = math.cos(twist)
                    s = math.sin(twist)
                    rx = x_mm * c - y_mm * s
                    ry = x_mm * s + y_mm * c
                    
                    val = tri_gyroid(rx, ry, z_mm, base_scale)
                    
                    # Threshold
                    # Lower threshold = Thinner walls = More transparent
                    # Range of tri_gyroid is approx [-2.4, 2.4]
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
    output_file = "base_v30.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
