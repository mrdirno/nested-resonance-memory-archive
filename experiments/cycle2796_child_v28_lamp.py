import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V28 (Catalog #93): THE AMMANN-BEENKER (Quasicrystal)
# -----------------------------------------------------------------------------
# Concept: An aperiodic tiling projected into 3D.
#          Based on 8-fold symmetry (Octagonal Quasicrystal).
#          Uses a Sum of Cosines (Density Wave) approximation.
# Parents: 38_penrose_tiling (5-fold), 12_crystalline_matrix (Structure).
# Math: Sum_{n=0}^{3} cos( (x cos(n pi/4) + y sin(n pi/4)) * k )
# -----------------------------------------------------------------------------

def ammann_beenker_approx(x, y, z):
    # Project 4 plane waves at 45 degree intervals (pi/4)
    # Vectors: (1,0), (1/rt2, 1/rt2), (0,1), (-1/rt2, 1/rt2)
    
    # Z modulation to make it 3D
    # Twist the whole tiling
    
    k = 1.0
    
    # Wave 1 (0 deg)
    w1 = math.cos(x * k)
    
    # Wave 2 (45 deg)
    rt2 = math.sqrt(2)
    # x*cos45 + y*sin45 = (x+y)/rt2
    w2 = math.cos((x + y) / rt2 * k)
    
    # Wave 3 (90 deg)
    w3 = math.cos(y * k)
    
    # Wave 4 (135 deg)
    # x*cos135 + y*sin135 = (-x+y)/rt2
    w4 = math.cos((-x + y) / rt2 * k)
    
    # Sum
    val = w1 + w2 + w3 + w4
    
    # Modulate Z
    # Simple lattice in Z?
    # val += math.cos(z * k) 
    # This makes it cubic-ish.
    
    # Let's make it extruded but twisted
    return val

def generate_child_v28(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V28 (The Ammann-Beenker): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 25.0
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # Scale
    # Quasicrystal features need to be visible
    base_scale = 2.0 * math.pi / 12.0 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist the tiling
        twist = z_mm * 0.02
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # 1. MOUNTING
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
                
                # 2. SHELL
                if z_mm < 4.0:
                    hand_radius = radius - shell_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    # 3. QUASICRYSTAL LATTICE
                    
                    # Rotate Coords
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    val = ammann_beenker_approx(x_rot * base_scale, y_rot * base_scale, z_mm * base_scale)
                    
                    # Threshold
                    # Increased for connectivity
                    t = 1.0
                    
                    # Modulate Z to create horizontal layers
                    # Lower freq Z modulation
                    val += math.cos(z_mm * base_scale * 0.5)
                    
                    if abs(val) < t:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                        
                else:
                     grid[x_idx,y_idx,z_idx] = False

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_93_ammann_beenker.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v28(output_file)
