import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V38 (Catalog #103): THE MINKOWSKI SAUSAGE (Fractal Box)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the Minkowski Sausage (a variant of the Koch curve
#          that uses squares instead of triangles).
#          Creates a blocky, fortress-like aesthetic.
# Parents: 16_mandelbrot (Fractal), 31_peano (Square).
# Math: L-System F -> F+F-F-FF+F+F-F
# -----------------------------------------------------------------------------

def generate_minkowski_curve(iterations):
    # Minkowski Sausage L-System (Type 2)
    # Generator: A square pulse.
    # Axiom: F
    # Rule: F -> F+F-F-FF+F+F-F
    # Angle: 90
    
    axiom = "F"
    seq = axiom
    
    for i in range(iterations):
        new_seq = ""
        for char in seq:
            if char == "F":
                # F+F-F-FF+F+F-F
                new_seq += "F+F-F-FF+F+F-F"
            else:
                new_seq += char
        seq = new_seq
        
    # Points
    current_pos = np.array([0.0, 0.0])
    current_dir = np.array([1.0, 0.0])
    points = [current_pos]
    
    step_size = 1.0
    
    for char in seq:
        if char == "F":
            current_pos = current_pos + current_dir * step_size
            points.append(current_pos)
        elif char == "+": # Left 90
            current_dir = np.array([-current_dir[1], current_dir[0]])
        elif char == "-": # Right 90
            current_dir = np.array([current_dir[1], -current_dir[0]])
            
    return np.array(points)

def generate_child_v38(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V38 (The Minkowski Sausage): {output_path}")

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
    # MINKOWSKI GENERATION
    # ---------------------------------------------------------
    
    # Iteration 3 is sufficiently complex
    points_2d = generate_minkowski_curve(3)
    
    # Normalize
    min_p = np.min(points_2d, axis=0)
    max_p = np.max(points_2d, axis=0)
    range_p = max_p - min_p
    
    norm_points = (points_2d - min_p) / range_p
    
    sphere_points = []
    
    for p in norm_points:
        u, v = p
        
        # Map to sphere
        # We want a "Fortress" look, so maybe less twist?
        # Map to Cylindrical first, then Sphere?
        # Let's stick to standard spherical mapping.
        
        theta = u * math.pi
        phi = v * 2.0 * math.pi
        
        # No twist, emphasizing the blocky nature
        
        sx = radius * math.sin(theta) * math.cos(phi)
        sy = radius * math.sin(theta) * math.sin(phi)
        sz = radius * math.cos(theta) + sphere_z_center
        
        sphere_points.append(np.array([sx, sy, sz]))
        
    print("Painting Minkowski Sausage...")
    
    # Tube is square? Or round?
    # A square tube fits the aesthetic better, but round is safer for interpolation.
    # Let's use round but thick.
    
    tube_radius = 6.0
    
    # Voxel Painting
    for k in range(len(sphere_points) - 1):
        p1 = sphere_points[k]
        p2 = sphere_points[k+1]
        
        dist = np.linalg.norm(p2 - p1)
        steps = max(1, int(dist / (step * 0.5)))
        
        for t in range(steps + 1):
            factor = t / steps
            p = p1 + (p2 - p1) * factor
            
            # Re-project
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
            
            brush = 4
            
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
                        d = math.sqrt((vx-p_surf[0])**2 + (vy-p_surf[1])**2 + (vz-p_surf[2])**2)
                        
                        # Spherical brush for better corner fusion
                        # Increased radius for connectivity
                        if d < 12.0:
                            grid[ix, iy, iz] = True

    # 1. MOUNTING
    print("Applying Mounting...")
    for z_idx in range(res_z):
        z_mm = z_idx * step
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                # REINFORCEMENT CAGE
                # Vertical bars to hold disconnected fractal islands
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                if dist_xy < radius and z_mm > 10.0:
                    # 40mm spacing, 4mm thick
                    if (abs(x_mm) % 40.0 < 4.0) and (abs(y_mm) % 40.0 < 4.0):
                         grid[x_idx,y_idx,z_idx] = True
                
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
                if dist_xy < 30.0 and z_mm > 10.0:
                    # Solid pillar with windows
                    if z_idx % 6 != 0: 
                        grid[x_idx,y_idx,z_idx] = True
                        
                # Bottom Rim
                if z_mm < 8.0:
                    if dist_xy < radius and dist_xy > (radius - shell_thickness):
                        grid[x_idx,y_idx,z_idx] = True

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_103_minkowski_sausage.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v38(output_file)
