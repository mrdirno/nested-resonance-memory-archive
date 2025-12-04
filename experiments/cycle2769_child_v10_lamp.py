import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V10: THE FRACTAL SINGULARITY (Multi-Octave Gyroid)
# -----------------------------------------------------------------------------
# Concept: A recursive accumulation of matter. The structure exhibits self-similarity.
#          It mimics the infinite complexity of a singularity or a fractal sponge.
# Parents: 03_singularity, 20_fractal.
# Math: Sum( Amplitude[i] * Gyroid( Frequency[i] * p ) )
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return np.sin(x) * np.cos(y) + np.sin(y) * np.cos(z) + np.sin(z) * np.cos(x)

def generate_child_v10(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V10 (The Fractal Singularity): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 22.0
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # Fractal Parameters
    # Octave 1 (Base Structure)
    scale_1 = 2.0 * math.pi / 35.0 # Large voids
    amp_1 = 1.0
    
    # Octave 2 (Detail)
    scale_2 = scale_1 * 2.0
    amp_2 = 0.5
    
    # Octave 3 (Texture)
    scale_3 = scale_1 * 4.0
    amp_3 = 0.25
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist
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
                    # 3. FRACTAL LATTICE
                    
                    # Apply Twist
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Fractal Sum (FBM)
                    g1 = gyroid(x_rot * scale_1, y_rot * scale_1, z_mm * scale_1)
                    g2 = gyroid(x_rot * scale_2, y_rot * scale_2, z_mm * scale_2)
                    g3 = gyroid(x_rot * scale_3, y_rot * scale_3, z_mm * scale_3)
                    
                    # Combined Field
                    # We can subtract higher frequencies to "erode" the base
                    # or add them to "build up".
                    # Standard FBM is addition.
                    val = g1 * amp_1 + g2 * amp_2 + g3 * amp_3
                    
                    # Normalize max amplitude estimate (1 + 0.5 + 0.25 = 1.75)
                    # Gyroid range is approx [-1.5, 1.5]
                    
                    # Variable Threshold
                    # Thicker at bottom
                    t_base = 0.8
                    t_mod = 0.2 * math.sin(z_mm * 0.05)
                    threshold = t_base + t_mod
                    
                    if abs(val) < threshold:
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
    output_file = os.path.join(output_dir, "child_v10_fractal_singularity.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v10(output_file)
