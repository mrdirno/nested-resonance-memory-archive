import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V50 (Catalog #115): THE DE RHAM CURVE (Corner Cutting)
# -----------------------------------------------------------------------------
# Concept: A continuous fractal curve constructed by iteratively cutting corners
#          of a polygon (similar to Chaikin's algorithm).
#          Projected onto a sphere, it creates a smooth yet complex "rounded
#          fractal" look.
# Parents: 32_dragon (Fractal), 18_nautilus (Curve).
# Math: Iterated affine transformations (De Rham system).
# -----------------------------------------------------------------------------

def generate_de_rham_curve(iterations=6):
    # De Rham Curve generation via corner cutting
    # Start with a square or polygon
    
    points = [
        np.array([0.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([1.0, 1.0]),
        np.array([0.0, 1.0]),
        np.array([0.0, 0.0]) # Closed loop
    ]
    
    # Cutting ratio
    # w = 1/3 creates the standard Chaikin curve (Quadratic B-Spline)
    # w = 1/4 creates something sharper
    w = 0.25
    
    for k in range(iterations):
        new_points = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i+1]
            
            # Cut corners
            # Q = (1-w)P0 + wP1
            # R = wP0 + (1-w)P1
            
            q = (1.0 - w) * p0 + w * p1
            r = w * p0 + (1.0 - w) * p1
            
            new_points.append(q)
            new_points.append(r)
            
        # Close loop
        new_points.append(new_points[0])
        points = new_points
        
    return np.array(points)

def generate_child_v50(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V50 (The De Rham Curve): {output_path}")

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
    # DE RHAM LATTICE
    # ---------------------------------------------------------
    
    # Generate curve (2D)
    # We want a complex initial polygon to get a fractal look.
    # A star shape?
    
    # Initial Star
    initial_points = []
    num_arms = 8
    for i in range(num_arms * 2):
        angle = (i / (num_arms * 2)) * 2.0 * math.pi
        r = 1.0 if i % 2 == 0 else 0.4
        initial_points.append(np.array([r * math.cos(angle), r * math.sin(angle)]))
    initial_points.append(initial_points[0])
    
    # Iterative Corner Cutting
    points = initial_points
    w = 0.2 # Sharper cuts
    
    iterations = 6
    for k in range(iterations):
        new_points = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i+1]
            
            q = (1.0 - w) * p0 + w * p1
            r = w * p0 + (1.0 - w) * p1
            
            new_points.append(q)
            new_points.append(r)
        new_points.append(new_points[0])
        points = new_points
        
    points_2d = np.array(points)
    
    # Map to Sphere
    # Center is (0,0). Range approx [-1, 1].
    # Map to (theta, phi) on top hemisphere?
    # Or map to (theta, z) on cylinder?
    
    # Let's map to stereographic projection on top?
    # Or just (x,y) -> (x,y) project to z?
    
    # Map to Cylinder Surface
    # theta = angle(p)
    # z = radius(p) scaled
    
    sphere_points = []
    
    for p in points_2d:
        # Map 2D (x,y) to 3D (theta, z)
        # We wrap the curve around the cylinder
        
        # u = angle
        # v = radius (height)
        
        u = math.atan2(p[1], p[0])
        dist_2d = math.sqrt(p[0]**2 + p[1]**2)
        
        v = dist_2d # 0 to 1 approx
        
        # Cylinder mapping
        theta = u # Wrap around
        
        # Spiral twist
        theta += v * 4.0 # Multiple wraps
        
        # Height
        # z from bottom to top
        z_val = v * height
        
        # Radius is constant?
        # r = radius
        
        # Cartesian
        sx = radius * math.cos(theta)
        sy = radius * math.sin(theta)
        sz = z_val
        
        # Scale Z to fit
        # Norm v is 0 to 1? Star goes to 1.0.
        # But cutting smooths it.
        
        # Re-center Z
        sz = sz + (height * 0.1) # Lift up
        
        if sz > 0 and sz < height:
            sphere_points.append(np.array([sx, sy, sz]))
            
    print("Painting De Rham Curve...")
    
    # Paint
    tube_radius = 5.0
    
    for k in range(len(sphere_points) - 1):
        p1 = sphere_points[k]
        p2 = sphere_points[k+1]
        
        dist = np.linalg.norm(p2 - p1)
        if dist > 50.0: continue # Skip wrap-around jumps if any
        
        steps = max(1, int(dist / (step * 0.5)))
        
        for t in range(steps + 1):
            factor = t / steps
            p = p1 + (p2 - p1) * factor
            
            # Project to surface
            # r = radius
            # But we are already on radius.
            
            gx = int((p[0] + radius) / step)
            gy = int((p[1] + radius) / step)
            gz = int(p[2] / step)
            
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
                        
                        d = math.sqrt((vx-p[0])**2 + (vy-p[1])**2 + (vz-p[2])**2)
                        
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
                    
                # Lattice Support
                # De Rham curve is a single thread. Needs support.
                
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
                        
                        if abs(g_val) < 0.2:
                            grid[x_idx,y_idx,z_idx] = True

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_115_de_rham_curve.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v50(output_file)
