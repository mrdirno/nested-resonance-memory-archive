import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V41 (Catalog #106): THE APOLLONIAN FOAM (Spherical Packing)
# -----------------------------------------------------------------------------
# Concept: A 3D foam structure based on the Apollonian Gasket (tangent circles).
#          Instead of a single layer like the Steiner Chain, this is a recursive
#          packing of spheres within spheres, or extruded circles.
# Parents: 40_apollonian_gasket (2D), 87_voronoi_foam (3D Foam).
# Math: Recursive Descartes Circle Theorem or KIFS (Kleinian Group).
# -----------------------------------------------------------------------------

def generate_child_v41(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V41 (The Apollonian Foam): {output_path}")

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
    # APOLLONIAN GASKET GENERATION (Simplified)
    # ---------------------------------------------------------
    
    # We generate a list of circles (cylinders) or spheres.
    # Let's do a 2D Apollonian Gasket extruded vertically with a twist/pulse.
    
    circles = []
    
    # Level 0: Main circle (Outer boundary) - Radius R
    # We pack inside this.
    
    # Level 1: 3 mutually tangent circles inscribed in R
    # Curvature k = 1/r
    # Descartes Theorem: (k1+k2+k3+k4)^2 = 2(k1^2+k2^2+k3^2+k4^2)
    # For symmetric start:
    # Outer curvature k0 = -1/R
    # 3 Inner circles with same curvature k1.
    # k1 = k0 * (1 + 2/sqrt(3)) ? No.
    # For 3 symmetric circles in a circle:
    # r_inner = R * (2*sqrt(3) - 3) approx 0.464 R
    
    r0 = radius * 0.9 # Working radius
    
    # Magic ratio for 3 circles fitting in 1
    # r = R * (1 / (1 + 2/sqrt(3))) ?
    # sin(30) = 0.5.
    # r / (R-r) = sin(60)? No.
    
    # Center of small circle is at dist D = R - r
    # Distance between centers is 2r
    # 2r = sqrt(3) * D (Triangle height geometry)
    # 2r = sqrt(3) * (R - r)
    # 2r = sqrt(3)R - sqrt(3)r
    # r(2 + sqrt(3)) = sqrt(3)R
    # r = R * sqrt(3) / (2 + sqrt(3)) = R * 0.4641
    
    ratio = math.sqrt(3) / (2.0 + math.sqrt(3))
    r1 = r0 * ratio
    
    dist_center = r0 - r1
    
    # Add 3 level-1 circles
    for i in range(3):
        angle = i * (2.0 * math.pi / 3.0)
        cx = dist_center * math.cos(angle)
        cy = dist_center * math.sin(angle)
        circles.append((cx, cy, r1))
        
    # Add center circle? (Soddy circle)
    # The hole between the 3 circles.
    # Using Descartes theorem k4.
    # k1 = 1/r1. k2=k1, k3=k1.
    # k4 = k1 + k2 + k3 + 2*sqrt(k1k2 + k2k3 + k3k1)
    # k4 = 3k1 + 2*sqrt(3 k1^2) = 3k1 + 2*sqrt(3)*k1 = k1(3 + 2sqrt(3))
    
    k1 = 1.0 / r1
    k_center = k1 * (3.0 + 2.0 * math.sqrt(3.0))
    r_center = 1.0 / k_center
    circles.append((0.0, 0.0, r_center))
    
    # Now we have gaps between (Outer, C1, C2) etc.
    # We can iterate Descartes to fill gaps.
    # This generates infinite circles.
    # We'll stop at a min radius.
    
    queue = []
    # Generate triplets of tangent circles to find the 4th
    # (Outer, C1, C2) -> Gap1
    # (Outer, C2, C3) -> Gap2
    # (Outer, C3, C1) -> Gap3
    # (C1, C2, Center) -> Gap4 ...
    
    # Actually, implementing full Apollonian recursion is complex.
    # Let's stick to a fixed set of recursive placements or a random packing.
    
    # Let's try "Random Apollonian Packing"
    # Try to place circle. If it overlaps, shrink.
    # Or "Apollonian Gasket via Inversion (KIFS)"
    
    # Let's stick to the generated list so far and maybe subdivide them.
    # Just recursing the "3-circle" pattern inside the circles?
    # Self-similar. 
    
    # Recursive function
    def recurse_circles(cx, cy, r, depth):
        if depth == 0: return
        if r < 2.0: return # Min features size
        
        # Sub-circles
        sub_r = r * ratio
        sub_dist = r - sub_r
        
        # Rotate orientation by 60 deg to fill better?
        offset_angle = (depth % 2) * (math.pi / 3.0)
        
        for i in range(3):
            angle = i * (2.0 * math.pi / 3.0) + offset_angle
            scx = cx + sub_dist * math.cos(angle)
            scy = cy + sub_dist * math.sin(angle)
            circles.append((scx, scy, sub_r))
            recurse_circles(scx, scy, sub_r, depth-1)
            
        # Center sub-circle
        # Small one in middle
        sub_k = (1.0/sub_r) * (3.0 + 2.0 * math.sqrt(3.0))
        sub_cr = 1.0 / sub_k
        circles.append((cx, cy, sub_cr))
        
    # Run recursion on the level 1 circles
    for cx, cy, r in list(circles): # Copy list
        recurse_circles(cx, cy, r, 2)
        
    print(f"Generated {len(circles)} circles for foam structure.")
    
    # Optimize: Spatial Hash?
    # Brute force for ~100 circles is fine.
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist the foam
        twist = z_mm * 0.015
        
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
                    x_mm, y_mm, z_mm,
                    dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue
                
                spider_check = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm,
                    dist_xy,
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
                    # 3. APOLLONIAN LATTICE
                    
                    # Rotate coords
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Check if inside any circle wall
                    in_wall = False
                    
                    # Optimization: only check nearby circles?
                    # Just iterate.
                    
                    for cx, cy, r in circles:
                        d = math.sqrt((x_rot-cx)**2 + (y_rot-cy)**2)
                        
                        # Wall thickness logic
                        # We want the circles to be empty tubes (foam).
                        # Wall is at r.
                        # thickness scaled by r?
                        t = max(1.5, r * 0.15)
                        
                        if abs(d - r) < t:
                            in_wall = True
                            break
                            
                    # Also add a Gyroid binder
                    base_scale = 2.0 * math.pi / 20.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                            
                    is_gyroid = abs(g_val) < 0.3
                    
                    if in_wall or is_gyroid:
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
    output_file = os.path.join(output_dir, "child_106_apollonian_foam.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v41(output_file)
