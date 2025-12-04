import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V33 (Catalog #98): THE DRAGON SPHERE (Projected Fractal)
# -----------------------------------------------------------------------------
# Concept: The Dragon Curve (Heighway Dragon) is a space-filling-ish fractal.
#          We project a 2D Dragon Curve onto the surface of a sphere.
# Parents: 32_dragon_curve (2D), 23_geodesic_dome (Sphere).
# Math: Iterative function system (IFS) projected to spherical coords.
# -----------------------------------------------------------------------------

def generate_dragon_curve(iterations):
    # Generate Dragon Curve points (2D)
    # Start with a segment
    points = [np.array([0.0, 0.0]), np.array([1.0, 0.0])]
    
    for i in range(iterations):
        new_points = []
        for j in range(len(points) - 1):
            p1 = points[j]
            p2 = points[j+1]
            
            # Vector
            v = p2 - p1
            
            # Rotate 45 degrees and scale by 1/sqrt(2)
            # x' = (x - y)/sqrt(2)?
            # Actually simpler: Rotate 90 deg, scale 0.5?
            # Standard geometric construction:
            # Replace segment with two segments forming a right triangle.
            
            # Midpoint M
            # M = p1 + v/2 + rotate90(v)/2 ?
            
            # If j is even/odd (direction flips)
            # Dragon curve flips direction every segment?
            # Actually, it's easier to fold.
            
            # Let's use the "Fold" algorithm on a list of turns.
            # No, let's stick to geometric substitution.
            # Left turn, Right turn...
            pass
            
    # Let's use the sequence approach.
    # R
    # R R L
    # R R L R R L L
    # ...
    
    sequence = []
    for i in range(iterations):
        # Next sequence = sequence + [R] + reversed(inverted(sequence))
        # R = 1, L = -1
        r = [1]
        inv = [-x for x in sequence[::-1]]
        sequence = sequence + r + inv
        
    # Now generate points
    current_pos = np.array([0.0, 0.0])
    current_dir = np.array([1.0, 0.0]) # East
    
    points_2d = [current_pos]
    
    for turn in sequence:
        # Move forward
        current_pos = current_pos + current_dir
        points_2d.append(current_pos)
        
        # Turn
        # turn is 1 (Right) or -1 (Left)
        # Rotate vector 90 deg
        if turn == 1: # Right
            current_dir = np.array([current_dir[1], -current_dir[0]])
        else: # Left
            current_dir = np.array([-current_dir[1], current_dir[0]])
            
    # One last move
    current_pos = current_pos + current_dir
    points_2d.append(current_pos)
    
    return np.array(points_2d)

def generate_child_v33(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V33 (The Dragon Sphere): {output_path}")

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
    # DRAGON CURVE GENERATION
    # ---------------------------------------------------------
    
    iterations = 12 # 4096 segments? sequence length 2^n - 1
    # 2^12 = 4096 points.
    # Too sparse for Voxel Painting?
    # 4000 points is low density.
    # But we can interpolate.
    
    points_2d = generate_dragon_curve(iterations)
    
    # Map 2D points to Sphere Surface
    # We map (x, y) to (theta, phi)
    # Normalize 2D range
    min_p = np.min(points_2d, axis=0)
    max_p = np.max(points_2d, axis=0)
    range_p = max_p - min_p
    
    norm_points = (points_2d - min_p) / range_p # 0 to 1
    
    # Map to spherical coverage
    # Theta: 0 to Pi
    # Phi: 0 to 2Pi
    
    # We want to wrap it around the sphere.
    # Use Fibonacci sphere mapping?
    # Or direct mapping.
    
    sphere_points = []
    
    for p in norm_points:
        u, v = p
        
        # Map to sphere
        theta = u * math.pi       # Pole to Pole
        phi = v * 2.0 * math.pi * 2.0 # Wrap twice? Or once?
        
        # To cover sphere better, Dragon fits in a square roughly.
        # Let's wrap phi 0 to 2pi.
        phi = v * 2.0 * math.pi
        
        # Adjust theta to avoid pole singularity issues visually?
        theta = theta * 0.9 + 0.05 * math.pi
        
        # Spherical to Cartesian
        sx = radius * math.sin(theta) * math.cos(phi)
        sy = radius * math.sin(theta) * math.sin(phi)
        sz = radius * math.cos(theta) + sphere_z_center
        
        sphere_points.append(np.array([sx, sy, sz]))
        
    # Paint Trajectory
    # Interpolate segments
    
    print("Painting Dragon Curve...")
    
    tube_radius = 5.0 # Thick curve
    
    # Pre-calc grid indices for speed?
    # No, simple interpolation loop.
    
    for k in range(len(sphere_points) - 1):
        p1 = sphere_points[k]
        p2 = sphere_points[k+1]
        
        # Arc interpolation (Geodesic)?
        # Linear interpolation is fine for small steps.
        # 4096 steps on a sphere surface is small enough.
        
        dist = np.linalg.norm(p2 - p1)
        steps = max(1, int(dist / (step * 0.5)))
        
        for t in range(steps + 1):
            factor = t / steps
            p = p1 + (p2 - p1) * factor
            
            # Project back to radius to ensure it stays on shell?
            # Linear interp cuts through sphere volume.
            # Re-normalize to radius relative to center.
            
            rel_z = p[2] - sphere_z_center
            current_r = math.sqrt(p[0]**2 + p[1]**2 + rel_z**2)
            
            # Push to surface
            # p_surf = p * (radius / current_r) # No, z offset.
            
            # Vector from center
            vec = np.array([p[0], p[1], rel_z])
            vec_len = np.linalg.norm(vec)
            if vec_len > 0:
                vec_norm = vec / vec_len
                p_surf = vec_norm * radius
                p_surf[2] += sphere_z_center
            else:
                p_surf = p
                
            # Grid index
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
                        
                        # Physical
                        vx = (ix * step) - radius
                        vy = (iy * step) - radius
                        vz = iz * step
                        
                        # Dist to point
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
                    
                # Central Column for Dragon support?
                # Dragon curve is self-intersecting in projection?
                # No, Dragon fills space.
                # But on a sphere, it might need support if it's just a surface winding.
                # A central pillar ensures it doesn't collapse.
                if dist_xy < 15.0 and z_mm > 10.0:
                    # Grid-like pillar
                    if z_idx % 4 != 0: 
                        grid[x_idx,y_idx,z_idx] = True

    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_98_dragon_curve.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v33(output_file)
