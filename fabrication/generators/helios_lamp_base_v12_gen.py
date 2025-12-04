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
# HELIOS LAMP SERIES V12: THE EVENTUALITY (BASE)
# -----------------------------------------------------------------------------
# Concept: Data Rot (Lattice dissolution).
# Math: Gyroid with Noise-modulated Threshold.
# -----------------------------------------------------------------------------

def noise_3d(x, y, z, seed=42):
    # Simple pseudo-random noise
    # Not true Perlin, but enough for static decay
    val = math.sin(x*0.1 + seed) * math.cos(y*0.13 + seed*2) * math.sin(z*0.07 + seed*3)
    return val

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating V12 BASE (Data Rot): {output_path}")

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
    
    base_scale = 2.0 * math.pi / 20.0
    decay_start_radius = 30.0 # Core is intact

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

                # V2 Socket Interface
                socket_check = lamp_lib.apply_base_socket_v2(z_mm, dist, height)
                if socket_check is False:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # Body Logic
                if dist <= radius:
                    # Solid Core
                    if dist < 25.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    if dist > radius: continue
                    
                    if (z_mm < 2.0) or (z_mm > height - 2.0) or (dist > radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                    # Base Gyroid
                    gx = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale)
                    gy = math.sin(y_mm * base_scale) * math.cos(z_mm * base_scale)
                    gz = math.sin(z_mm * base_scale) * math.cos(x_mm * base_scale)
                    val = gx + gy + gz
                    
                    # Decay Logic
                    # Decay increases with distance from center
                    decay_factor = (dist - decay_start_radius) / (radius - decay_start_radius)
                    if decay_factor < 0: decay_factor = 0
                    
                    noise = noise_3d(x_mm, y_mm, z_mm)
                    
                    # Threshold shrinks as decay increases, eroding the structure
                    # Or noise adds "holes"
                    
                    threshold = 0.5
                    
                    # Apply decay: If noise is high and decay is high, reduce threshold (erosion)
                    # Or simply: val += noise * decay_factor
                    
                    eroded_val = val + (noise * decay_factor * 1.5)
                    
                    if abs(eroded_val) < threshold:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "base_v12.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
