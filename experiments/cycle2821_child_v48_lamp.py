import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V48 (Catalog #113): THE PYTHAGORAS TREE (Fractal Branching)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the Pythagoras Tree fractal.
#          Recursive squares forming a tree-like structure.
#          Projected onto a sphere or cylinder.
# Parents: 112_barnsley (Botany), 107_t_square (Squares).
# Math: Recursive geometry (Pythagorean Theorem construction).
# -----------------------------------------------------------------------------

def generate_pythagoras_tree(iterations=10):
    # Generate 2D squares
    # List of squares: (center_x, center_y, size, angle)
    # Or (p1, p2) of base.
    
    # Start with base square at (0,0) to (1,0)
    squares = []
    
    # Stack: (p1, p2, depth)
    # p1 is bottom-left, p2 is bottom-right of the square's base
    stack = [(np.array([0.0, 0.0]), np.array([1.0, 0.0]), 0)]
    
    while stack:
        p1, p2, depth = stack.pop()
        
        # Vector base
        v = p2 - p1
        length = np.linalg.norm(v)
        
        # Top points of square
        # Rotate -90 (left) from v
        perp = np.array([-v[1], v[0]])
        
        p3 = p2 + perp # Top-right
        p4 = p1 + perp # Top-left
        
        # Store square (p1, p2, p3, p4)
        # Or just center and size for point cloud?
        # Let's store the quad for rasterization?
        # Point cloud is easier for our "Voxel Painting" pipeline.
        # Sample points inside the square?
        
        # Let's just store the center and size, and paint it later.
        center = (p1 + p2 + p3 + p4) / 4.0
        squares.append((center, length, math.atan2(v[1], v[0])))
        
        if depth < iterations:
            # Construct triangle on top (p4, p3)
            # Right isosceles triangle? Or 30-60-90?
            # Standard is 45-45-90.
            
            # New vertex P_top forms right angle
            # Midpoint of (p4, p3) is M
            # P_top is M + perp(p3-p4)/2
            
            v_top = p3 - p4
            perp_top = np.array([-v_top[1], v_top[0]])
            
            mid = (p4 + p3) / 2.0
            p_apex = mid + perp_top / 2.0
            
            # Left branch: Base is (p4, p_apex)
            stack.append((p4, p_apex, depth+1))
            
            # Right branch: Base is (p_apex, p3)
            stack.append((p_apex, p3, depth+1))
            
    return squares

def generate_child_v48(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V48 (The Pythagoras Tree): {output_path}")

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
    # TREE GENERATION
    # ---------------------------------------------------------
    
    # Iteration 8 is dense enough
    squares = generate_pythagoras_tree(8)
    
    # Normalize
    # Collect all centers to find bounds
    centers = np.array([s[0] for s in squares])
    min_p = np.min(centers, axis=0)
    max_p = np.max(centers, axis=0)
    range_p = max_p - min_p
    
    print("Mapping Tree to Sphere...")
    
    # Map to sphere
    # We want the tree to wrap around.
    # X -> Phi, Y -> Theta
    
    sphere_points = []
    
    # Place 4 trees
    num_trees = 4
    
    for i in range(num_trees):
        offset_phi = (i / num_trees) * 2.0 * math.pi
        
        for center, size, angle in squares:
            # Norm 0-1
            u = (center[0] - min_p[0]) / range_p[0]
            v = (center[1] - min_p[1]) / range_p[1]
            
            # Map
            theta = (1.0 - v) * math.pi # Bottom to top
            theta = theta * 0.8 + 0.1 # Clamp
            
            phi_width = math.pi / 2.0
            phi = (u - 0.5) * phi_width + offset_phi
            
            # Twist
            phi += theta * 0.3
            
            sx = radius * math.sin(theta) * math.cos(phi)
            sy = radius * math.sin(theta) * math.sin(phi)
            sz = radius * math.cos(theta) + sphere_z_center
            
            # Store point and size
            # Scale size based on sphere radius?
            # size is relative to range_p.
            # physical_size = (size / range_p[0]) * (phi_width * radius)
            
            phys_size = (size / range_p[0]) * 100.0 # approx scale factor
            
            sphere_points.append((np.array([sx, sy, sz]), phys_size))
            
    print("Painting Pythagoras Tree...")
    
    # Voxel Painting
    # Iterate grid or points?
    # For squares, we have center and size. We can paint a cube/sphere at that location.
    
    # To optimize, we can iterate points.
    
    for center, size in sphere_points:
        gx = int((center[0] + radius) / step)
        gy = int((center[1] + radius) / step)
        gz = int(center[2] / step)
        
        # Brush size based on square size
        # Ensure minimum thickness
        r_brush = max(4.0, size * 0.8)
        
        brush = int(r_brush / step) + 1
        
        for bx in range(-brush, brush+1):
            ix = gx + bx
            if ix < 0 or ix >= res_x: continue
            for by in range(-brush, brush+1):
                iy = gy + by
                if iy < 0 or iy >= res_y: continue
                for bz in range(-brush, brush+1):
                    iz = gz + bz
                    if iz < 0 or iz >= res_z: continue
                    
                    if grid[ix, iy, iz]: continue
                    
                    vx = (ix * step) - radius
                    vy = (iy * step) - radius
                    vz = iz * step
                    
                    # Distance
                    d = math.sqrt((vx-center[0])**2 + (vy-center[1])**2 + (vz-center[2])**2)
                    
                    if d < r_brush:
                        grid[ix, iy, iz] = True

    # 1. MOUNTING
    print("Applying Mounting...")
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
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                cap = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap is not None:
                    grid[x_idx,y_idx,z_idx] = cap
                    continue
                    
                spider = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider is not None:
                    grid[x_idx,y_idx,z_idx] = spider
                    
                # Substrate Lattice (to hold small squares)
                # Pythagoras tree leaves get very small and disconnected?
                # Actually, squares touch. But rasterization might leave gaps.
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    if not grid[x_idx,y_idx,z_idx]:
                        # Background lattice
                        base_scale = 2.0 * math.pi / 20.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        if abs(g_val) < 0.45:
                            grid[x_idx,y_idx,z_idx] = True
                        # Horizontal Ribs
                        elif z_mm % 30.0 < 3.0:
                            grid[x_idx,y_idx,z_idx] = True

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_113_pythagoras_tree.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v48(output_file)
