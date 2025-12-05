import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V51 (Catalog #116): THE MINKOWSKI QUESTION MARK (Fractal Function)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the Minkowski ?(x) function (a singular function).
#          It maps rationals to dyadic rationals and irrationals to everything else.
#          The curve is a "Devil's Staircase".
# Parents: 118_cantor_function (Staircase), 114_blancmange (Pathological).
# Math: Continued Fraction Expansion recursion.
# -----------------------------------------------------------------------------

def minkowski_question_mark(x, depth=10):
    # ?(x) function
    # Uses continued fraction representation
    # x = [0; a1, a2, a3, ...]
    # ?(x) = sum (-1)^(k+1) / 2^(sum(ai for i=1 to k)-1)
    
    # Simplified recursive definition for [0,1]:
    # If x < 1/2, ?(x) = ?(2x/(1-x)) / 2 ? No, that's not right.
    
    # Farey Sequence approach (Stern-Brocot Tree)
    # Find where x lies in the Stern-Brocot tree.
    
    # p/q and p'/q' are endpoints. m/n = (p+p')/(q+q') is mediant.
    # If x < m/n, go left. If x > m/n, go right.
    # Left child value is (V_left + V_mediant)/2 ?
    
    # Let's use a simple recursive approximation.
    
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    if depth == 0: return x # Linear approx at limit
    
    # Mediant search
    # Start with 0/1 and 1/1. Mediant 1/2.
    # Val 0, 1. Mediant Val 1/2.
    
    a, b = 0, 1 # 0/1
    c, d = 1, 1 # 1/1
    
    val_a = 0.0
    val_c = 1.0
    
    for i in range(depth):
        # Mediant
        m = a + c
        n = b + d
        mid = m / n
        val_mid = (val_a + val_c) / 2.0
        
        if x == mid:
            return val_mid
        elif x < mid:
            # Go Left: (a/b, m/n)
            c, d = m, n
            val_c = val_mid
        else:
            # Go Right: (m/n, c/d)
            a, b = m, n
            val_a = val_mid
            
    return (val_a + val_c) / 2.0

def generate_child_v51(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V51 (The Minkowski Question Mark): {output_path}")

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
    # QUESTION MARK LATTICE
    # ---------------------------------------------------------
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist
        twist = z_mm * 0.02
        
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
                    # 3. FRACTAL PATTERN
                    
                    # Rotate
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Map to U, V
                    theta = math.atan2(y_rot, x_rot)
                    u = (theta + math.pi) / (2.0 * math.pi)
                    
                    # Scale U to 0-1 over sections?
                    # Let's repeat it 3 times.
                    u_scaled = (u * 3.0) % 1.0
                    
                    # Z height
                    z_local = (z_mm / height) * 3.0 # 3 vertical bands?
                    z_local = z_local % 1.0
                    
                    # Eval ?(x)
                    # The function ?(x) maps x to y.
                    # It creates a staircase.
                    # We can create walls where z_local < ?(u_scaled).
                    # Or create a thin shell at z_local = ?(u_scaled).
                    
                    q_val = minkowski_question_mark(u_scaled, depth=12)
                    
                    # Create a ribbon
                    # Thickness
                    t = 0.2
                    
                    # Shift
                    # q_val is 0 to 1.
                    
                    # We want a lattice.
                    # Let's use the derivative? No, deriv is 0 or inf.
                    # Let's use the proximity to the curve.
                    
                    diff = abs(z_local - q_val)
                    
                    if diff < t:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Secondary lattice
                        base_scale = 2.0 * math.pi / 15.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Thicker lattice
                        if abs(g_val) < 0.45:
                            grid[x_idx,y_idx,z_idx] = True
                        # Vertical Ribs
                        elif (u * 16.0) % 1.0 < 0.1:
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
    output_file = os.path.join(output_dir, "child_116_minkowski_question_mark.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v51(output_file)
