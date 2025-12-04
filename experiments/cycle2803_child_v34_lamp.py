import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V34 (Catalog #99): THE KOCH SNOWFLAKE (Fractal Extrusion)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the famous Koch Snowflake fractal curve.
#          To make it "Jaw Dropping", the extrusion is twisted along the Z-axis
#          and modulated by a second fractal (Mandelbrot) density function.
# Parents: 16_mandelbrot (Fractal), 53_involute_spiral (Extrusion).
# Math: Distance to 2D Koch polygon + Z-Twist.
# -----------------------------------------------------------------------------

def koch_snowflake_distance(x, y, iterations=4):
    # Approximate distance to Koch Snowflake boundary.
    # Since exact distance is hard, we use a symmetry-folding approach.
    # Symmetry group: 3-fold or 6-fold.
    
    # Pre-scale
    # Start with a triangle.
    
    # Fold space to a 30-degree sector (1/12th)?
    # Koch snowflake has 6-fold symmetry.
    
    # Let's use a simplified Iterated Function System (IFS) "Fold and Scale".
    
    px, py = x, y
    
    # Center
    px = abs(px)
    py = abs(py) # 4-fold symmetry fold first
    
    # Not quite right for 6-fold.
    # Let's use polar coords.
    
    r = math.sqrt(x*x + y*y)
    if r == 0: return 0.0
    angle = math.atan2(y, x)
    
    # Map to sector [0, pi/3]
    sector = math.pi / 3.0
    angle = angle % sector
    if angle > sector / 2.0:
        angle = sector - angle
        
    # Back to cartesian
    px = r * math.cos(angle)
    py = r * math.sin(angle)
    
    # Now iterate the Koch logic
    # "Fold" across the line y = tan(30)*x ? No.
    
    # Standard KIFS (Kaleidoscopic IFS) approach for Koch:
    # Plane normals
    n1 = np.array([math.sin(math.pi/3), math.cos(math.pi/3)]) # 30 deg? no 60.
    # This is getting complex to implement inline.
    
    # Alternative: Use a "Snowflake" lattice via Fourier Series?
    # Sum cos(k*theta)?
    
    # Let's use a "Snowflake" field approximation:
    # r = R * (1 + A * sum( ... ))
    
    # r = 1 + 0.3*cos(6*theta) + 0.1*cos(18*theta) + 0.03*cos(54*theta) ...
    
    max_r = 1.0
    
    # Base 6-fold
    # Harmonic series
    # Amplitude decays as 3^-n?
    
    perturbation = 0.0
    amp = 0.25
    freq = 6.0
    
    for i in range(iterations):
        perturbation += amp * math.cos(angle * freq)
        amp *= 0.4 # Decay
        freq *= 3.0 # Koch frequency step
        
    boundary = 1.0 + perturbation
    
    # Signed distance (approx)
    dist = r - boundary
    
    return dist

def generate_child_v34(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V34 (The Koch Snowflake): {output_path}")

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
    
    # Scale
    # Normalized coords used in fractal function
    scale = 1.0 / (radius * 0.7) 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Vertical Twist
        twist = z_mm * 0.03
        
        # Vertical "Pulse" (Zoom)
        # The snowflake grows and shrinks
        zoom = 1.0 + 0.3 * math.sin(z_mm * 0.05)
        
        current_scale = scale / zoom
        
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
                    # 3. FRACTAL LATTICE
                    
                    # Apply Twist
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Calculate distance field to Snowflake boundary
                    d_frac = koch_snowflake_distance(x_rot * current_scale, y_rot * current_scale)
                    
                    # Threshold
                    # d_frac = 0 is the boundary
                    # d_frac < 0 is inside, > 0 is outside
                    # We want a lattice ON the boundary
                    
                    # Wall thickness
                    # Thickened
                    t_fractal = 0.15
                    
                    is_fractal_wall = abs(d_frac) < t_fractal
                    
                    # Secondary Gyroid (The Binder)
                    base_scale = 2.0 * math.pi / 15.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    # Thickened for connectivity
                    is_lattice = abs(g_val) < 0.45
                    
                    # Union Logic:
                    # Fractal Wall OR Lattice
                    if is_fractal_wall or is_lattice:
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
    output_file = os.path.join(output_dir, "child_99_koch_snowflake.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v34(output_file)
