import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V25: THE FUTURIST (SHADE)
# -----------------------------------------------------------------------------
# Concept: Cyber Dome (Geodesic/Hex).
# Math: Hexagonal Field.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating V25 SHADE (Cyber Dome): {output_path}")

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
    
    base_scale = 2.0 * math.pi / 30.0
    
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

                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue

                spider_check = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider_check is not None:
                    grid[x_idx,y_idx,z_idx] = spider_check
                    continue

                if z_mm < 4.0:
                    hand_radius = radius - wall_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue

                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - wall_thickness)
                in_hand = (dist_xy < (radius - wall_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand:
                    # Hexagonal Logic (Approximation)
                    # sin(x+y) * sin(x-y) * sin(y)
                    
                    # Rotate to get better hex alignment on sphere?
                    # Just use 3-plane intersection
                    
                    val = math.sin(x_mm * base_scale) * math.sin(y_mm * base_scale) * math.sin(z_mm * base_scale)
                    
                    # Or straight lines
                    is_x = abs(math.sin(x_mm * base_scale)) < 0.2
                    is_y = abs(math.sin(y_mm * base_scale)) < 0.2
                    is_z = abs(math.sin(z_mm * base_scale)) < 0.2
                    
                    # This makes a Cubic Grid.
                    # For Hex, we need 60 deg lines.
                    
                    # Rotated Grid 1
                    r1 = x_mm * 0.5 - y_mm * 0.866
                    is_r1 = abs(math.sin(r1 * base_scale)) < 0.2
                    
                    # Rotated Grid 2
                    r2 = x_mm * 0.5 + y_mm * 0.866
                    is_r2 = abs(math.sin(r2 * base_scale)) < 0.2
                    
                    # Combine X + R1 + R2 -> Hexagonal in XY plane
                    # Extrude in Z? Or dome it?
                    
                    if is_x or is_r1 or is_r2:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                         grid[x_idx,y_idx,z_idx] = False
                else:
                     grid[x_idx,y_idx,z_idx] = False

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shade_v25.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
