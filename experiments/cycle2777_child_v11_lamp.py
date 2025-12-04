import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V11 (Gen 22): THE GLITCH LATTICE (Pixel Sorted Gyroid)
# -----------------------------------------------------------------------------
# Concept: A mathematical structure suffering from digital corruption.
#          The lattice is "sorted" or displaced along axes based on noise,
#          mimicking datamoshing or VRAM failure.
# Parents: 27_gyroid_lattice (Base), 23_glitch (Corruption).
# Math: Gyroid( p + Discontinuous_Step(p) )
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return np.sin(x) * np.cos(y) + np.sin(y) * np.cos(z) + np.sin(z) * np.cos(x)

def glitch_displacement(x, y, z, block_size=10.0):
    # Quantize coordinates to create "blocks"
    # Shift blocks randomly along X or Y based on Z
    
    # Block ID
    bx = np.floor(x / block_size)
    by = np.floor(y / block_size)
    bz = np.floor(z / (block_size * 0.5)) # Thinner vertical slices
    
    # Pseudo-random hash for block shift
    # Deterministic noise
    h = np.sin(bx * 12.9898 + by * 78.233 + bz * 151.7182) * 43758.5453
    h = h - np.floor(h) # 0.0 to 1.0
    
    # Probability of glitch
    # Higher probability near top
    glitch_prob = (z / 140.0) * 0.8 
    
    shift_x = 0.0
    
    # If hash < prob, apply shift
    # We perform this element-wise if x,y,z are arrays, but here we iterate or use numpy
    # Since we are inside a loop in generating code usually, let's assume scalar or careful numpy usage.
    # Wait, the generator usually iterates. We can keep it simple scalar for now.
    
    if h < glitch_prob:
        # Magnitude of shift
        shift_x = (h - 0.5) * 20.0 # +/- 10mm
        
    return shift_x

def generate_child_v11(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V11 (The Glitch Lattice): {output_path}")

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
    
    # Scale
    base_scale = 2.0 * math.pi / 25.0 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Calculate glitch shift for this Z-slice? 
        # Pixel sorting usually happens row by row.
        # Let's do block-based shifting inside the loop.
        
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
                    # 3. GLITCH LATTICE
                    
                    # Compute Shift
                    # We use x,y,z to determine block ID
                    shift = glitch_displacement(x_mm, y_mm, z_mm)
                    
                    # Apply shift to X coordinate (Pixel Sort effect)
                    x_shifted = x_mm + shift
                    
                    # Evaluate Gyroid
                    g_val = gyroid(x_shifted * base_scale, y_mm * base_scale, z_mm * base_scale)
                    
                    # Threshold
                    t = 0.4
                    
                    if abs(g_val) < t:
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
    output_file = os.path.join(output_dir, "child_v11_glitch_lattice.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v11(output_file)
