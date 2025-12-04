import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V11: THE HYPER-DIMENSIONAL (SHADE)
# -----------------------------------------------------------------------------
# Concept: Dimensional Rift (Self-intersecting Surface).
# Math: 4D Gyroid Projection.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating V11 SHADE (Dimensional Rift): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    hub_radius = 20.0
    spoke_width = 8.0
    wall_thickness = 25.4
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 4
    res_y = int(diameter / step) + 4
    res_z = int(height / step) + 1
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    base_scale = 2.0 * math.pi / 40.0
    
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
                in_hand = (dist_xy < (radius - wall_thickness)) and (z_mm <= spider_z_start)
                
                if in_outer and not in_inner and not in_hand:
                    # 4D Projection Logic
                    # We define 'w' based on radial distance from center of sphere
                    # This creates "shells" of varying 4D cross-sections
                    
                    w = dist_spherical * 0.1
                    
                    lx = x_mm * base_scale
                    ly = y_mm * base_scale
                    lz = z_mm * base_scale
                    lw = w * base_scale
                    
                    # 4D Gyroid Approximation
                    val = math.cos(lx+lw) + math.cos(ly-lw) + math.cos(lz+lw)
                    
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
    output_file = "shade_v11.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
