import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V3: THE IMPOSSIBLE FLOW (Escher + Swarm)
# -----------------------------------------------------------------------------
# Concept: A rigid geometric lattice (Escher/Penrose) that is being 
#          liquefied by a vortex field.
# Parents: 26_impossible (Geometry) + 14_swarm (Motion).
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return math.sin(x) * math.cos(y) + math.sin(y) * math.cos(z) + math.sin(z) * math.cos(x)

def generate_child_v3(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V3 (The Impossible Flow): {output_path}")

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
    
    # Scale for the "Impossible" Geometry
    base_scale = 2.0 * math.pi / 30.0 # Increased period for robust connections
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # ---------------------------------------------------------
        # SWARM DISTORTION FIELD
        # ---------------------------------------------------------
        # A vortex that gets stronger near the top, breaking the geometry
        vortex_strength = (z_mm / height) * 0.5
        vortex_freq = 0.1
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # 1. MOUNTING HARDWARE
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
                
                # 2. SHELL DEFINITION
                if z_mm < 4.0:
                    hand_radius = radius - shell_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    # 3. IMPOSSIBLE LATTICE GENERATION
                    
                    # Apply Vortex Warp
                    angle = math.atan2(y_mm, x_mm)
                    radius_warp = dist_xy * (1.0 + vortex_strength * math.sin(angle * 6.0 + z_mm * vortex_freq))
                    
                    x_warp = radius_warp * math.cos(angle + vortex_strength)
                    y_warp = radius_warp * math.sin(angle + vortex_strength)
                    z_warp = z_mm + (math.sin(dist_xy * 0.1) * 5.0) # Ripple Z
                    
                    # Switched to Gyroid for guaranteed connectivity
                    val = gyroid(x_warp * base_scale, y_warp * base_scale, z_warp * base_scale)
                    
                    # Thresholding
                    # FIX: Changed to Wall logic (abs < t) to ensure connectivity.
                    # Previous Node logic (> t) created isolated floating islands.
                    
                    threshold = 0.5 + (0.15 * math.sin(z_mm * 0.05))
                    
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
    output_file = os.path.join(output_dir, "child_v3_impossible_flow.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v3(output_file)
