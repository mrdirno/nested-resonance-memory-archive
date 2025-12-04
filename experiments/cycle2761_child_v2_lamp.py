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
# CHILD V2: THE LIQUID GYROID (AGPH + FLUID DYNAMICS)
# -----------------------------------------------------------------------------
# Concept: A lattice that appears to be melting or flowing under gravity.
# Parent: Favorites V36 & V12.
# Math: Gyroid domain warped by a vertical flow field.
# -----------------------------------------------------------------------------

def gyroid(x, y, z):
    return math.sin(x) * math.cos(y) + math.sin(y) * math.cos(z) + math.sin(z) * math.cos(x)

def generate_child_v2(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V2 (The Liquid Gyroid): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    # Shell thickness where the lattice lives
    shell_thickness = 30.0 
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # AGPH Parameters
    # Higher frequency for a denser "foam" look that flows
    base_scale = 2.0 * math.pi / 22.0 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Flow Distortion (The "Liquid" effect)
        # As Z increases (goes up), the flow is less distorted (source).
        # As Z decreases (goes down), the distortion accumulates (pooling).
        flow_strength = (1.0 - (z_mm / height)) * 8.0 # 0 to 8mm distortion at bottom
        
        # Vertical "Drip" stretching
        z_stretch = 1.0 + (0.5 * math.sin(z_mm * 0.05))
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z for sphere projection (Macro Shape)
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # ---------------------------------------------------------
                # 1. MOUNTING HARDWARE (SOLID & MANDATORY)
                # ---------------------------------------------------------
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                # Solid Cap for stability
                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue
                
                # Spider Fitter (Hub + Spokes)
                spider_check = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider_check is not None:
                    grid[x_idx,y_idx,z_idx] = spider_check
                    continue
                
                # ---------------------------------------------------------
                # 2. MACRO SHELL DEFINITION
                # ---------------------------------------------------------
                # Bottom opening for hand access
                if z_mm < 4.0:
                    hand_radius = radius - shell_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True # Solid Rim
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    # -----------------------------------------------------
                    # 3. FLUID LATTICE GENERATION
                    # -----------------------------------------------------
                    
                    # Apply Flow Distortion to coordinates
                    # "Swirl" the domain
                    angle = math.atan2(y_mm, x_mm)
                    swirl = flow_strength * math.sin(z_mm * 0.1)
                    
                    x_flow = x_mm + math.cos(angle + swirl) * flow_strength
                    y_flow = y_mm + math.sin(angle + swirl) * flow_strength
                    z_flow = z_mm * z_stretch
                    
                    # Evaluate Gyroid
                    g_val = gyroid(x_flow * base_scale, y_flow * base_scale, z_flow * base_scale)
                    
                    # Dynamic Thresholding (Breath)
                    # Thicker at bottom (structural), Thinner at top (light)
                    # BUT modulated by a "Pulse" to open up windows
                    
                    base_t = 0.45
                    pulse = 0.25 * math.sin(z_mm * 0.15) * math.cos(angle * 3.0)
                    
                    final_threshold = base_t + pulse
                    
                    # Clamp to ensure connectivity (never go below 0.15 or above 0.9)
                    final_threshold = max(0.15, min(0.9, final_threshold))
                    
                    if abs(g_val) > final_threshold:
                        grid[x_idx,y_idx,z_idx] = False # Void
                    else:
                        grid[x_idx,y_idx,z_idx] = True # Solid
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
    output_file = os.path.join(output_dir, "child_v2_liquid.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v2(output_file)
