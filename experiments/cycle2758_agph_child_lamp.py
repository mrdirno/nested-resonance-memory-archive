import numpy as np
import math
import sys
import os

# Add project root to path
# Current: experiments/
# Root:    ../
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V1: THE RESPIRATORY LATTICE (AGPH IMPLEMENTATION)
# -----------------------------------------------------------------------------
# Concept: A breathing lattice that expands and contracts its porosity.
# Parent: V33 (Oracle Sphere) & AGPH Theory.
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return math.sin(x) * math.cos(y) + math.sin(y) * math.cos(z) + math.sin(z) * math.cos(x)

def generate_child(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating CHILD V1 (The Respiratory Lattice): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    wall_thickness_base = 25.4 # Reference from V33 (Shell thickness)
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid to avoid clipping
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # AGPH Parameters
    base_period = 30.0 # Slightly larger for flow
    base_scale = 2.0 * math.pi / base_period
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Vertical Breathing Factor (Z-modulation)
        breath_phase = z_mm * 0.05
        scale_mod = 1.0 + 0.3 * math.sin(breath_phase)
        current_scale = base_scale * scale_mod
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # Effective Z for sphere projection
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # 1. MOUNTING LOGIC (CRITICAL - DO NOT MODIFY)
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
                # Hand access at bottom
                if z_mm < 4.0:
                    hand_radius = radius - wall_thickness_base
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - wall_thickness_base)
                # Keep-out zone for hand (cylinder in center)
                in_hand = (dist_xy < (radius - wall_thickness_base)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand:
                    # 3. AGPH LATTICE GENERATION
                    # Twist factor (Helical)
                    twist = z_mm * 0.02
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Evaluate Gyroid
                    g_val = gyroid(x_rot * current_scale, y_rot * current_scale, z_mm * current_scale)
                    
                    # Modulate Threshold for "Breathing" density
                    # ROBUSTIFIED: Increased thickness to ~4mm physical (t=0.6) to resolve in 2mm grid
                    base_t = 0.6
                    mod_t = 0.2 * math.sin(z_mm * 0.1) # Gentle breathing vertical
                    final_threshold = base_t + mod_t # Range 0.4 to 0.8
                    
                    if abs(g_val) > final_threshold: # Wall condition
                        grid[x_idx,y_idx,z_idx] = False # Void
                    else:
                        grid[x_idx,y_idx,z_idx] = True # Solid (Wall)
                else:
                     grid[x_idx,y_idx,z_idx] = False

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    # Default output path relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_v1_respiratory.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child(output_file)