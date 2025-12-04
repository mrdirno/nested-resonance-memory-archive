import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V10: THE EVENT HORIZON (SHADE)
# -----------------------------------------------------------------------------
# Concept: Gravitational Lensing (Warped Field).
# Math: Radial Domain Warping + Gyroid.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating V10 SHADE (Lensing Flare): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    hub_radius = 20.0
    spoke_width = 8.0
    
    wall_thickness = 25.4 # 1 inch
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 4
    res_y = int(diameter / step) + 4
    res_z = int(height / step) + 1
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    base_scale = 2.0 * math.pi / 30.0 # Larger pattern
    
    spider_z_start = height - 40.0

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
                
                # Current radius at this Z (for cap logic)
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0

                # 1. Cap Logic
                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue

                # 2. Spider Fitter
                if z_mm > spider_z_start:
                    if dist_xy < hub_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    spoke_half = spoke_width / 2.0
                    d1 = abs(y_mm)
                    d2 = abs(math.sqrt(3)*x_mm - y_mm) / 2.0
                    d3 = abs(math.sqrt(3)*x_mm + y_mm) / 2.0
                    
                    if d1 < spoke_half or d2 < spoke_half or d3 < spoke_half:
                        if dist_xy < radius:
                            grid[x_idx,y_idx,z_idx] = True
                            continue

                # 3. Bottom Rim
                if z_mm < 4.0:
                    hand_radius = radius - wall_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                # 4. Body
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - wall_thickness)
                
                # Hand access void (Z < Spider Start)
                in_hand = (dist_xy < (radius - wall_thickness)) and (z_mm <= spider_z_start)
                
                if in_outer and not in_inner and not in_hand:
                    # Lensing Warp
                    # Warp magnitude increases towards the "black hole" (center of sphere volume)
                    # Actually, let's warp towards the Z-axis
                    
                    warp_mag = 10.0 * (1.0 - (dist_xy / radius))
                    
                    # Radial displacement
                    angle = math.atan2(y_mm, x_mm)
                    wx = x_mm + math.cos(angle) * warp_mag
                    wy = y_mm + math.sin(angle) * warp_mag
                    
                    lx = wx * base_scale
                    ly = wy * base_scale
                    lz = z_mm * base_scale
                    
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    if abs(val) < 0.5:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                         grid[x_idx,y_idx,z_idx] = False
                else:
                     grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shade_v10.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
