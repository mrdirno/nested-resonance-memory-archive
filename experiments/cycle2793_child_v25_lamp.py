import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V25 (Catalog #90): THE SCHWARZSCHILD WARP (Gravitational Lensing)
# -----------------------------------------------------------------------------
# Concept: A regular grid that is severely distorted by a simulated Black Hole.
#          The lattice lines bend and stretch as if light is being pulled 
#          into a singularity at the center.
# Parents: 04_event_cascade (Singularity), 19_galaxy_spiral (Orbit).
# Math: Schwarzschild metric deflection approx: alpha = 4GM / (c^2 * b)
#       We map p' -> p + distortion(p)
# -----------------------------------------------------------------------------

def lensing_warp(x, y, z, radius_event_horizon=25.0):
    # Distance from center (Singularity)
    r = math.sqrt(x*x + y*y + z*z)
    
    # Avoid div by zero
    r_safe = max(1.0, r)
    
    # Deflection angle/strength
    # Stronger near horizon, weaker far away.
    # Standard lensing is 1/r.
    
    strength = radius_event_horizon / r_safe
    
    # "Pinch" distortion:
    # Pull points towards center? No, lensing magnifies background.
    # So we push points OUTWARD from center to simulate magnification of the lattice behind the hole?
    # Or pull INWARD to show the hole itself?
    
    # Let's pull INWARD to stretch the lattice into the hole.
    # New R = R - strength * factor
    
    # Actually, a "Vortex" pull is more dramatic.
    # Combine radial pull with twist. 
    
    # Logarithmic pull
    pull = math.log(r_safe / radius_event_horizon) 
    # If r < horizon, pull is negative (inside).
    
    # Let's use a simple non-linear radial warp.
    # r_new = r^k
    
    # r_new = r - (1000.0 / (r^2))
    
    # Let's try to simulate the "Einstein Ring" effect.
    # The lattice creates a ring at the Einstein radius.
    
    # Milder warp to preserve lattice integrity
    warp_factor = 1.0 + (30.0 / r_safe)
    
    # Apply warp to coordinates
    # This expands the central region (magnification)
    x_new = x * warp_factor
    y_new = y * warp_factor
    z_new = z * warp_factor
    
    return x_new, y_new, z_new

def generate_child_v25(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V25 (The Schwarzschild Warp): {output_path}")

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
    
    # Lensing Center (The Singularity)
    # Located inside the sphere, slightly up.
    bh_z = height * 0.6
    
    # Base Lattice (Grid)
    # Simple cubic grid to show distortion clearly.
    # Or a Gyroid for better structure. Gyroid is better.
    base_scale = 2.0 * math.pi / 20.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
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
                    # 3. SCHWARZSCHILD LATTICE
                    
                    # Center coordinates on BH
                    x_rel = x_mm
                    y_rel = y_mm
                    z_rel = z_mm - bh_z
                    
                    # Apply Lensing Warp
                    wx, wy, wz = lensing_warp(x_rel, y_rel, z_rel)
                    
                    # Evaluate Gyroid in warped space
                    val = np.sin(wx*base_scale) * np.cos(wy*base_scale) + \
                          np.sin(wy*base_scale) * np.cos(wz*base_scale) + \
                          np.sin(wz*base_scale) * np.cos(wx*base_scale)
                          
                    # Threshold
                    # We want to thicken the lattice near the "Event Horizon" (center)
                    # because the warp stretches it thin.
                    
                    # Distance from BH in unwarped space
                    d_bh = math.sqrt(x_rel**2 + y_rel**2 + z_rel**2)
                    
                    # Adaptive threshold
                    # Base thickness
                    t = 0.5
                    
                    # If close to BH, increase threshold to compensate for stretching
                    if d_bh < 60.0:
                        t += 0.8 * (1.0 - d_bh/60.0)
                        
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
    output_file = os.path.join(output_dir, "child_90_schwarzschild_warp.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v25(output_file)
