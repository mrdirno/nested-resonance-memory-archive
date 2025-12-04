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
# HELIOS LAMP SERIES V12: THE EVENTUALITY (SHADE)
# -----------------------------------------------------------------------------
# Concept: Bit Rot (Missing Chunks).
# Math: Boolean Subtraction of Noise Spheres.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating V12 SHADE (Bit Rot): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    wall_thickness = 25.4
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 4
    res_y = int(diameter / step) + 4
    res_z = int(height / step) + 1
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    base_scale = 2.0 * math.pi / 25.0
    
    # Noise Field for "Rot"
    # Simple seeded random
    random.seed(12345)
    
    # Pre-calculate noise map? Too heavy.
    # Use simple sin/cos interference as "noise" to subtract chunks
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0

                # 1. Cap Logic (Protected)
                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue

                # 2. Spider Fitter (Protected)
                spider_check = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider_check is not None:
                    grid[x_idx,y_idx,z_idx] = spider_check
                    continue

                # 3. Bottom Rim (Protected)
                if z_mm < 4.0:
                    hand_radius = radius - wall_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                # 4. Body
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - wall_thickness)
                # Hand access logic handled by wall thickness check above?
                # Wait, if we just check shells, we get a hollow sphere.
                # We need an OPENING at the bottom.
                # The sphere center is at Height - Radius.
                # Bottom is Z=0.
                # If Height=140 and Radius=100, Center=40.
                # Bottom Z=0 is below center.
                # Sphere equation naturally closes.
                # We need to cut the bottom opening explicitly if the sphere goes lower than Z=0.
                # But here Z goes 0..Height.
                
                # Let's assume the standard "Bell" shape is implicitly handled by the loop bounds
                # and the fact that we only fill if inside the sphere.
                # If we want a bottom opening, we need to mask it.
                # Hand Access radius:
                in_hand = (dist_xy < (radius - wall_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand:
                    # Base Gyroid
                    val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                          math.sin(y_mm * base_scale) * math.cos(z_mm * base_scale) + \
                          math.sin(z_mm * base_scale) * math.cos(x_mm * base_scale)
                    
                    is_solid = abs(val) < 0.55
                    
                    # Bit Rot Logic
                    # Subtract "chunks" randomly
                    # Chunk probability increases with distance from top
                    
                    rot_prob = 1.0 - (z_mm / height) # 1.0 at bottom, 0.0 at top
                    
                    # Large low-frequency noise for chunks
                    chunk_noise = math.sin(x_mm*0.05) + math.cos(y_mm*0.05) + math.sin(z_mm*0.05)
                    
                    if chunk_noise > (1.0 + (1.0-rot_prob)): # High threshold means rare chunks
                        is_solid = False
                        
                    if is_solid:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                         grid[x_idx,y_idx,z_idx] = False
                else:
                     grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shade_v12.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
