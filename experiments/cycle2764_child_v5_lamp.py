import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V5: THE CRYSTAL EROSION (Schwarz D + Noise)
# -----------------------------------------------------------------------------
# Concept: A pristine mathematical structure (Diamond Lattice) that is 
#          being reclaimed by nature (Noise Erosion) as it rises.
# Parents: 26_impossible (Order) + 12_growth (Chaos).
# -----------------------------------------------------------------------------

def schwarz_d(x, y, z):
    # Schwarz Diamond Surface
    return math.sin(x)*math.sin(y)*math.sin(z) + \
           math.sin(x)*math.cos(y)*math.cos(z) + \
           math.cos(x)*math.sin(y)*math.cos(z) + \
           math.cos(x)*math.cos(y)*math.sin(z)

def pseudo_noise(x, y, z):
    # A cheap deterministic noise function for erosion
    # Using high frequency sines
    n1 = math.sin(x * 0.5) * math.cos(y * 0.5) * math.sin(z * 0.5)
    n2 = math.sin(x * 1.3 + 1.0) * math.cos(y * 1.3 + 2.0) * math.sin(z * 1.3 + 3.0)
    return (n1 + n2 * 0.5) # Range approx [-1.5, 1.5]

def generate_child_v5(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V5 (The Crystal Erosion): {output_path}")

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
    
    # Scale for the Diamond Geometry
    base_scale = 2.0 * math.pi / 25.0 
    
    # Scale for Noise
    noise_scale = base_scale * 0.8
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Erosion Gradient (0.0 at bottom -> 1.0 at top)
        erosion_factor = (z_mm / height) ** 1.5 # Non-linear, accelerates at top
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Macro Shape: Sphere
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
                    # 3. ERODED LATTICE GENERATION
                    
                    # Base Structure (Diamond)
                    d_val = schwarz_d(x_mm * base_scale, y_mm * base_scale, z_mm * base_scale)
                    
                    # Erosion Field
                    n_val = pseudo_noise(x_mm * noise_scale, y_mm * noise_scale, z_mm * noise_scale)
                    
                    # Composite: Crystal - (Noise * Factor)
                    # We want the threshold to widen (decay) as we go up
                    
                    # Base Threshold for Diamond Wall
                    base_threshold = 0.6
                    
                    # Apply erosion: effectively shifting the iso-value
                    # If noise is positive, it subtracts from structure -> holes
                    composite_val = d_val - (n_val * erosion_factor * 1.5)
                    
                    if abs(composite_val) < base_threshold:
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
    output_file = os.path.join(output_dir, "child_v5_crystal_erosion.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v5(output_file)
