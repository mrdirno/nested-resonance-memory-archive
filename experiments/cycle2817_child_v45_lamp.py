import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V45 (Catalog #110): THE RAUZY FRACTAL (Tribonacci Tiling)
# -----------------------------------------------------------------------------
# Concept: A fractal domain associated with the Tribonacci substitution rule.
#          (1 -> 12, 2 -> 13, 3 -> 1).
#          It creates a complex, self-similar tiling of the plane.
# Parents: 101_gosper (Substitution), 38_penrose (Tiling).
# Math: Projected domain of a stepping plane in 3D grid (Rauzy Fractal).
# -----------------------------------------------------------------------------

def rauzy_fractal_approx(x, y, iterations=5):
    # The Rauzy fractal is the domain of the Tribonacci substitution.
    # It's complex to calculate exactly.
    # We can approximate it using a generalized "Raw" substitution or
    # simply a specific algebraic form.
    
    # Simplified Rauzy-like aesthetic:
    # Iterated substitution of 3 shapes (parallelograms/rectangles).
    # Or use the "Tribonacci Word" to drive a turtle?
    
    # Let's use a simpler visual proxy:
    # A recursive subdivision into 3 uneven parts.
    
    # Domain [0,1] x [0,1]
    # Split into 3 regions based on Tribonacci ratio T (approx 1.839).
    # 1/T = 0.543...
    # 1/T^2 = 0.295...
    # 1/T^3 = 0.160...
    
    # Just use a recursive block pattern that mimics the look.
    # Check iteration depth.
    
    cx = x
    cy = y
    
    # Tribonacci constant
    T = 1.83928675521
    inv_T = 1.0 / T # 0.543
    
    for i in range(iterations):
        # Split x and y
        # Map to 3 zones: [0, 1/T^2], [1/T^2, 1/T], [1/T, 1]
        # Lengths: 0.29, 0.24, 0.46
        
        t1 = 1.0 / (T**2)
        t2 = 1.0 / T
        
        # Transform
        if cx < t1:
            cx = cx / t1
            # Zone 1: Keep
        elif cx < t2:
            cx = (cx - t1) / (t2 - t1)
            # Zone 2: Hole?
            if i % 2 == 0: return False # Create holes
        else:
            cx = (cx - t2) / (1.0 - t2)
            # Zone 3: Keep
            
        if cy < t1:
            cy = cy / t1
        elif cy < t2:
            cy = (cy - t1) / (t2 - t1)
            if i % 2 != 0: return False
        else:
            cy = (cy - t2) / (1.0 - t2)
            
    return True

def generate_child_v45(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V45 (The Rauzy Fractal): {output_path}")

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
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist
        twist = z_mm * 0.025
        
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
                    # 3. RAUZY LATTICE
                    
                    # Rotate
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Map to UV
                    theta = math.atan2(y_rot, x_rot)
                    u = (theta + math.pi) / (2.0 * math.pi)
                    v = z_mm / height
                    
                    # Scale for pattern
                    u_scaled = (u * 3.0) % 1.0
                    v_scaled = (v * 2.0) % 1.0
                    
                    if rauzy_fractal_approx(u_scaled, v_scaled, iterations=4):
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Lattice in voids
                        base_scale = 2.0 * math.pi / 15.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Stronger lattice for connectivity
                        if abs(g_val) < 0.45:
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
    output_file = os.path.join(output_dir, "child_110_rauzy_fractal.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v45(output_file)
