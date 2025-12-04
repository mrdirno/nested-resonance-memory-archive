import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V36 (Catalog #101): THE GOSPER CURVE (Flowsnake)
# -----------------------------------------------------------------------------
# Concept: A space-filling curve on a hexagonal grid (The Gosper Island boundary).
#          Projected onto a sphere, it creates a dense, puzzle-piece aesthetic.
# Parents: 96_peano_curve (Space Filling), 38_penrose_tiling (Hex/5-fold).
# Math: L-System recursion.
# -----------------------------------------------------------------------------

def generate_gosper_curve(iterations):
    # Gosper Curve L-System
    # Axiom: A
    # Rules:
    # A -> A-B--B+A++AA+B-
    # B -> +A-BB--B-A++A+B
    # Angle: 60 degrees
    
    axiom = "A"
    seq = axiom
    
    for i in range(iterations):
        new_seq = ""
        for char in seq:
            if char == "A":
                new_seq += "A-B--B+A++AA+B-"
            elif char == "B":
                new_seq += "+A-BB--B-A++A+B"
            else:
                new_seq += char
        seq = new_seq
        
    # Convert to points
    points = [np.array([0.0, 0.0])]
    current_pos = np.array([0.0, 0.0])
    current_angle = 0.0
    step_size = 1.0
    
    for char in seq:
        if char == "A" or char == "B":
            # Move forward
            dx = step_size * math.cos(current_angle)
            dy = step_size * math.sin(current_angle)
            current_pos = current_pos + np.array([dx, dy])
            points.append(current_pos)
        elif char == "+":
            current_angle += math.pi / 3.0 # 60 deg
        elif char == "-":
            current_angle -= math.pi / 3.0
            
    return np.array(points)

def generate_child_v36(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V36 (The Gosper Curve): {output_path}")

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
    # GOSPER GENERATION
    # ---------------------------------------------------------
    
    # Iteration 4 gives a good complexity
    points_2d = generate_gosper_curve(4)
    
    # Normalize to map to sphere surface
    min_p = np.min(points_2d, axis=0)
    max_p = np.max(points_2d, axis=0)
    range_p = max_p - min_p
    
    norm_points = (points_2d - min_p) / range_p # 0 to 1
    
    # Map to Sphere
    sphere_points = []
    
    for p in norm_points:
        u, v = p
        
        # Map to spherical coords
        # Wrap around fully?
        # Gosper island is hexagonal. 
        # Let's map it to cover the hemisphere.
        
        theta = u * math.pi # 0 to Pi
        phi = v * 2.0 * math.pi 
        
        # Twist for flow
        twist = theta * 0.5
        phi += twist
        
        # Cartesian
        sx = radius * math.sin(theta) * math.cos(phi)
        sy = radius * math.sin(theta) * math.sin(phi)
        sz = radius * math.cos(theta) + sphere_z_center
        
        sphere_points.append(np.array([sx, sy, sz]))
        
    print("Painting Gosper Curve...")
    
    tube_radius = 4.0 # Wireframe thickness
    
    # Voxel Painting
    for k in range(len(sphere_points) - 1):
        p1 = sphere_points[k]
        p2 = sphere_points[k+1]
        
        dist = np.linalg.norm(p2 - p1)
        steps = max(1, int(dist / (step * 0.5)))
        
        for t in range(steps + 1):
            factor = t / steps
            p = p1 + (p2 - p1) * factor
            
            # Re-project to surface to maintain curvature
            rel_z = p[2] - sphere_z_center
            vec = np.array([p[0], p[1], rel_z])
            vec_len = np.linalg.norm(vec)
            if vec_len > 0:
                p_surf = (vec / vec_len) * radius
                p_surf[2] += sphere_z_center
            else:
                p_surf = p
            
            # Grid Index
            gx = int((p_surf[0] + radius) / step)
            gy = int((p_surf[1] + radius) / step)
            gz = int(p_surf[2] / step)
            
            brush = 3
            
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
                        
                        d = math.sqrt((vx-p_surf[0])**2 + (vy-p_surf[1])**2 + (vz-p_surf[2])**2)
                        
                        if d < tube_radius:
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
                    
                # Support Pillar
                if dist_xy < 15.0 and z_mm > 10.0:
                    if z_idx % 4 != 0: 
                        grid[x_idx,y_idx,z_idx] = True

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_101_gosper_curve.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v36(output_file)
