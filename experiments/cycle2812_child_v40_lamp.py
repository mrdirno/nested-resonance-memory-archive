import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V40 (Catalog #105): THE CANTOR DUST (Fractal Pillars)
# -----------------------------------------------------------------------------
# Concept: A 3D visualization of the Cantor Set (removing the middle third).
#          Extruded vertically to form a forest of pillars that disappear into
#          dust at the top.
# Parents: 45_menger_sponge (Fractal), 12_crystalline_matrix (Structure).
# Math: Recursive interval removal.
# -----------------------------------------------------------------------------

def cantor_set_density(x, y, z, iterations=5):
    # Cantor Set logic:
    # Divide interval [0, 1] into 3 parts.
    # Keep left and right, discard middle.
    # Repeat.
    
    # For 3D "Dust", we apply this to X and Y to get a grid of pillars.
    # And maybe apply it to Z inversely? Or fade it out?
    
    # Let's make the pillars dissolve as they go up.
    # At Z=0, iteration 0 (Solid block).
    # At Z=1, iteration 5 (Dust).
    
    # We assume inputs are normalized 0-1
    
    # Check X
    cx = x
    cy = y
    
    # Determine iteration level based on Z
    # z is 0 to 1.
    # Reduced max iterations for stability
    current_iter = int(z * (3 + 1))
    if current_iter > 3: current_iter = 3
    
    # But discrete steps are boring. Let's make it continuous?
    # Or just test if (x,y) belongs to Cantor Set at level N.
    
    def in_cantor(v, level):
        # Check if v is in the middle third at any level up to 'level'
        t = v
        for i in range(level):
            # Map t to 0-3
            t *= 3.0
            # Check middle (1 to 2)
            if t >= 1.0 and t <= 2.0:
                return False # Removed
            # Wrap
            t = t % 1.0
        return True
        
    is_x = in_cantor(cx, current_iter)
    is_y = in_cantor(cy, current_iter)
    
    if is_x and is_y:
        return True
    else:
        return False

def generate_child_v40(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V40 (The Cantor Dust): {output_path}")

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
    
    # ---------------------------------------------------------
    # CANTOR GENERATION
    # ---------------------------------------------------------
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Normalize Z for fractal calculation
        # 0 at bottom, 1 at top
        norm_z = z_mm / height
        
        # Twist to make it dynamic
        twist = norm_z * math.pi * 0.5
        
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
                    # 3. CANTOR LATTICE
                    
                    # Apply Twist
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Normalize to [0, 1] across diameter
                    # Range -R to +R -> 0 to 1
                    nx = (x_rot + radius) / diameter
                    ny = (y_rot + radius) / diameter
                    
                    # Bounds check for safety
                    if nx < 0 or nx > 1 or ny < 0 or ny > 1:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # Cantor Check
                    # Iterations increase with height?
                    # Or constant iteration?
                    # Let's use variable iteration to dissolve the shape.
                    
                    if cantor_set_density(nx, ny, norm_z, iterations=4):
                        # It's a pillar.
                        # But pillars will be disconnected "dust" at high Z.
                        # We need to connect them.
                        
                        # Option 1: Union with a Gyroid lattice?
                        # Option 2: Ensure "Dust" is actually connected via horizontal bridges?
                        
                        # Let's intersect with a Gyroid so the pillars aren't just square extrusions.
                        # Wait, the Cantor logic itself creates square pillars.
                        
                        # To fix connectivity of the "Dust":
                        # The Cantor Set is by definition disconnected.
                        # We must add horizontal connectors.
                        
                        # Add thin horizontal planes at interval boundaries?
                        # Or just Union with a weak Lattice.
                        
                        # Union logic
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Empty space
                        # Fill with lattice?
                        
                        # Secondary lattice to hold the dust
                        base_scale = 2.0 * math.pi / 15.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Thicker lattice for connectivity
                        if abs(g_val) < 0.35:
                            grid[x_idx,y_idx,z_idx] = True
                        
                        # Horizontal Floors (Binders)
                        # Every 20mm, 2mm thick
                        elif z_mm % 20.0 < 2.0:
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
    output_file = os.path.join(output_dir, "child_105_cantor_dust.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v40(output_file)
