import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V8: THE RECURSIVE FLOW (Domain Warped Gyroid)
# -----------------------------------------------------------------------------
# Concept: A Gyroid lattice subjected to recursive domain warping.
#          This creates a "Marbled" or "Liquid Jupiter" aesthetic where the
#          mathematical structure appears to be dissolving into turbulence.
# Parents: 14_swarm (Turbulence), 06_dark_matter (Web).
# Math: f(p) = Gyroid( p + A*Noise(p) )
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return np.sin(x) * np.cos(y) + np.sin(y) * np.cos(z) + np.sin(z) * np.cos(x)

def generate_child_v8(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V8 (The Recursive Flow): {output_path}")

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
    
    # Vectorized Grid Generation for Speed (FBM is heavy)
    # We'll create coordinate grids first
    x_range = np.linspace(-radius, radius, res_x) # Approx
    y_range = np.linspace(-radius, radius, res_y)
    z_range = np.linspace(0, height, res_z)
    
    # We will iterate to save memory, but perform vector ops per Z-slice or chunk
    
    # Scale
    base_scale = 2.0 * math.pi / 25.0 
    noise_scale = base_scale * 0.5
    warp_strength = 4.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Optimization: Skip if out of bounds vertically? No, complex shape.
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z for sphere
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
                    # 3. DOMAIN WARPED LATTICE
                    
                    # Base Coordinates
                    px = x_mm
                    py = y_mm
                    pz = z_mm
                    
                    # 1st Octave Noise (Vector)
                    # We use sines for cheap deterministic noise
                    nx = math.sin(px * noise_scale) + math.sin(py * noise_scale * 1.3)
                    ny = math.sin(py * noise_scale) + math.sin(pz * noise_scale * 1.3)
                    nz = math.sin(pz * noise_scale) + math.sin(px * noise_scale * 1.3)
                    
                    # Warp the domain
                    # The warp strength increases with Z to simulate "melting upwards" or "dissolving"
                    local_warp = warp_strength * (0.5 + 0.5 * math.sin(z_mm * 0.02))
                    
                    wx = px + nx * local_warp
                    wy = py + ny * local_warp
                    wz = pz + nz * local_warp
                    
                    # Evaluate Gyroid on Warped Domain
                    g_val = math.sin(wx * base_scale) * math.cos(wy * base_scale) + \
                            math.sin(wy * base_scale) * math.cos(wz * base_scale) + \
                            math.sin(wz * base_scale) * math.cos(wx * base_scale)
                    
                    # Threshold
                    # Standard Gyroid wall
                    t = 0.45
                    
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
    output_file = os.path.join(output_dir, "child_v8_recursive_flow.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v8(output_file)
