import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V26 (Catalog #91): THE STEINER CHAIN (Tangent Spheres)
# -----------------------------------------------------------------------------
# Concept: A necklace of spheres that touch each other and two boundary surfaces
#          (inner and outer shells). Based on Steiner's Porism.
#          The spheres spiral up the form, creating a bubble-bearing column.
# Parents: 40_apollonian_gasket (Tangency), 18_nautilus (Spiral).
# Math: Geometric placement of tangent spheres.
# -----------------------------------------------------------------------------

def generate_child_v26(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V26 (The Steiner Chain): {output_path}")

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
    # STEINER CHAIN GENERATION
    # ---------------------------------------------------------
    
    # We create a spiral of Steiner Chains.
    # Each layer is a ring of N spheres.
    # We rotate and lift the ring.
    
    spheres = []
    
    # Number of vertical layers
    num_layers = 12
    layer_height = height / num_layers
    
    for l in range(num_layers):
        z_layer = (l + 0.5) * layer_height
        
        # Adjust radius for macro sphere shape
        # Effective radius at this height
        # r_macro^2 + (z - center)^2 = R^2
        dz = z_layer - sphere_z_center
        if abs(dz) < radius:
            r_current = math.sqrt(radius**2 - dz**2)
        else:
            r_current = 10.0 # Cap
            
        # Ensure r_current is large enough for ring
        r_current = max(r_current, 40.0)
        
        # Steiner Chain Parameters
        # n spheres in ring
        n = 12
        
        # Radius of small spheres (r_s)
        # R_out = r_current
        # sin(pi/n) = r_s / (R_ring)
        # R_ring = R_out - r_s
        # r_s = (R_out - r_s) * sin(pi/n)
        # r_s = R_out * sin(pi/n) - r_s * sin(pi/n)
        # r_s (1 + sin) = R_out * sin
        # r_s = R_out * sin / (1 + sin)
        
        sin_val = math.sin(math.pi / n)
        r_s = r_current * sin_val / (1.0 + sin_val)
        
        # Center of ring
        r_ring = r_current - r_s
        
        # Twist angle
        twist = l * (math.pi / n) # Offset by half a sphere each layer?
        
        for i in range(n):
            angle = (i / n) * 2.0 * math.pi + twist
            
            cx = r_ring * math.cos(angle)
            cy = r_ring * math.sin(angle)
            cz = z_layer
            
            spheres.append((cx, cy, cz, r_s))
            
    # Add small connecting struts between spheres?
    # Or Union with a thin shell?
    # Let's union with a thin inner/outer lattice to hold them.
    
    # Let's compute.
    
    # Optimization: Bounding box check for spheres.
    
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
                    # 3. STEINER LATTICE
                    
                    # Check if inside any sphere
                    in_sphere = False
                    
                    # Optimization: Only check spheres in nearby Z layers
                    # (Skipping spatial hash for simplicity in this snippet, relies on list iteration)
                    # With 144 spheres, it's okay.
                    
                    for sx, sy, sz, sr in spheres:
                        # Quick Z check
                        if abs(z_mm - sz) > sr: continue
                        
                        d = math.sqrt((x_mm-sx)**2 + (y_mm-sy)**2 + (z_mm-sz)**2)
                        
                        # Hollow spheres?
                        # Shell of sphere: 0.8*sr < d < sr
                        if d < sr and d > (sr * 0.8):
                            in_sphere = True
                            break
                            
                    # Gyroid Backbone to connect them
                    base_scale = 2.0 * math.pi / 20.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    in_gyroid = abs(g_val) < 0.25
                    
                    if in_sphere or in_gyroid:
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
    output_file = os.path.join(output_dir, "child_91_steiner_chain.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v26(output_file)
