import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V29 (Catalog #94): THE BORROMEAN RINGS (Topological Link)
# -----------------------------------------------------------------------------
# Concept: Three rings linked in such a way that no two are linked, 
#          but the group is. A symbol of strength in unity.
# Parents: 50_torus_knot (Link), 34_lissajous (Geometry).
# Math: Three orthogonal elliptical tori.
# -----------------------------------------------------------------------------

def generate_child_v29(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V29 (The Borromean Rings): {output_path}")

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
    
    # Rings Configuration
    # We use 3 ellipses stretched along X, Y, and Z axes
    # Ratio 2:1
    
    ring_major = radius * 0.8
    ring_minor = radius * 0.4
    ring_tube = 12.0 # Thickness of the rings
    
    # Lattice for inside the rings (Wireframe look)
    base_scale = 2.0 * math.pi / 10.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Center Z for the link
        z_rel = z_mm - (height * 0.6) # Lifted slightly
        
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
                    # 3. BORROMEAN RINGS
                    
                    in_ring = False
                    
                    # Ring 1: XY Plane (Stretched X)
                    # Ellipse: (x/a)^2 + (y/b)^2 = 1
                    # Distance to ellipse is hard. Approximation:
                    # Map to torus coords with stretching?
                    # Simple Torus distance: sqrt( (r-R)^2 + z^2 )
                    # Stretched: r = sqrt( (x/2)^2 + y^2 ) * scale? No.
                    
                    # Implicit Elliptic Torus:
                    # ( sqrt( (x/a)^2 + (y/b)^2 ) - 1 )^2 + (z/c)^2 - r^2 = 0
                    
                    # Ring 1 (Flat): XY plane, stretched X
                    d1 = (math.sqrt((x_mm/ring_major)**2 + (y_mm/ring_minor)**2) - 1.0)**2 + (z_rel/ring_tube)**2
                    
                    # Ring 2 (Vertical): YZ plane, stretched Y
                    d2 = (math.sqrt((y_mm/ring_major)**2 + (z_rel/ring_minor)**2) - 1.0)**2 + (x_mm/ring_tube)**2
                    
                    # Ring 3 (Vertical): ZX plane, stretched Z
                    d3 = (math.sqrt((z_rel/ring_major)**2 + (x_mm/ring_minor)**2) - 1.0)**2 + (y_mm/ring_tube)**2
                    
                    # Threshold for Implicit Surface
                    # d < 0.2 approx
                    t_ring = 0.15
                    
                    if d1 < t_ring or d2 < t_ring or d3 < t_ring:
                        in_ring = True
                        
                    # Gyroid Lattice inside rings
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    is_lattice = abs(g_val) < 0.5 # Thicker lattice
                    
                    if in_ring and is_lattice:
                        grid[x_idx,y_idx,z_idx] = True
                    
                    # Bridge logic:
                    # If distance to rings < buffer, draw lattice
                    # Increased buffer/threshold for robust connection
                    
                    t_bridge = 1.5 # Wider field
                    if (d1 < t_bridge or d2 < t_bridge or d3 < t_bridge) and is_lattice:
                         grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Keep existing True if set by loop (mounting)
                        if not grid[x_idx,y_idx,z_idx]:
                            grid[x_idx,y_idx,z_idx] = False
                        
                else:
                     # Don't clear if set by mounting (already checked via continue, but safety)
                     if not grid[x_idx,y_idx,z_idx]:
                        grid[x_idx,y_idx,z_idx] = False

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_94_borromean_rings.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v29(output_file)
