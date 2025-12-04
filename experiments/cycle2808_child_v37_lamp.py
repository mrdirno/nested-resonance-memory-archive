import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V37 (Catalog #102): THE LEVY C CURVE (Fractal Construction)
# -----------------------------------------------------------------------------
# Concept: A self-similar fractal curve that tiles the plane.
#          Projected onto a sphere, it creates a dense, interlocking "C" pattern.
# Parents: 32_dragon_curve (Fractal), 101_gosper_curve (Space Filling).
# Math: IFS - Replace segment with two sides of isosceles triangle (45 deg).
# -----------------------------------------------------------------------------

def generate_levy_c_curve(iterations):
    # Start with a segment
    points = [np.array([0.0, 0.0]), np.array([1.0, 0.0])]
    
    for i in range(iterations):
        new_points = [points[0]]
        for j in range(len(points) - 1):
            p1 = points[j]
            p2 = points[j+1]
            
            # New point M forms a right isosceles triangle with p1, p2 as hypotenuse.
            # M = (p1 + p2)/2 + (Rotate90(p1-p2))/2
            
            mid = (p1 + p2) / 2.0
            vec = p2 - p1
            perp = np.array([-vec[1], vec[0]])
            
            m = mid - perp / 2.0 # "C" shape bulges one way
            
            new_points.append(m)
            new_points.append(p2)
            
        points = new_points
        
    return np.array(points)

def generate_child_v37(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V37 (The Levy C Curve): {output_path}")

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
    # LEVY C GENERATION
    # ---------------------------------------------------------
    
    # Iteration 14 gives higher density
    # 2^14 = 16384 segments
    
    points_2d = generate_levy_c_curve(14)
    
    # Normalize
    min_p = np.min(points_2d, axis=0)
    max_p = np.max(points_2d, axis=0)
    range_p = max_p - min_p
    
    # Levy C tends to grow "down/up" significantly
    
    norm_points = (points_2d - min_p) / range_p
    
    # Map to Sphere
    sphere_points = []
    
    for p in norm_points:
        u, v = p
        
        # Map u -> theta (0 to pi)
        # Map v -> phi (0 to 2pi)
        
        theta = u * math.pi
        phi = v * 2.0 * math.pi
        
        # Twist for 3D flow
        phi += theta * 0.8
        
        sx = radius * math.sin(theta) * math.cos(phi)
        sy = radius * math.sin(theta) * math.sin(phi)
        sz = radius * math.cos(theta) + sphere_z_center
        
        sphere_points.append(np.array([sx, sy, sz]))
        
    print("Painting Levy C Curve...")
    
    tube_radius = 6.5 # Thick wire to merge
    
    # Voxel Painting
    for k in range(len(sphere_points) - 1):
        p1 = sphere_points[k]
        p2 = sphere_points[k+1]
        
        dist = np.linalg.norm(p2 - p1)
        steps = max(1, int(dist / (step * 0.5)))
        
        for t in range(steps + 1):
            factor = t / steps
            p = p1 + (p2 - p1) * factor
            
            # Project to surface
            rel_z = p[2] - sphere_z_center
            vec = np.array([p[0], p[1], rel_z])
            vec_len = np.linalg.norm(vec)
            if vec_len > 0:
                p_surf = (vec / vec_len) * radius
                p_surf[2] += sphere_z_center
            else:
                p_surf = p
                
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
                # Thickened for stability
                if dist_xy < 20.0 and z_mm > 10.0:
                    if z_idx % 4 != 0: 
                        grid[x_idx,y_idx,z_idx] = True

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_102_levy_c_curve.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v37(output_file)
