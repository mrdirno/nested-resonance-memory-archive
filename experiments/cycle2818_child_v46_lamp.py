import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V46 (Catalog #111): THE BURNING SHIP (Fractal Extrusion)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the Burning Ship fractal.
#          Formula: z_{n+1} = (|Re(z_n)| + i|Im(z_n)|)^2 + c.
#          Known for its chaotic, flame-like, and ship-like structures.
# Parents: 16_mandelbrot (Mandelbrot set), 109_moran (Chaos).
# Math: Complex plane iteration with absolute values.
# -----------------------------------------------------------------------------

def burning_ship_distance(cx, cy, max_iter=20):
    # Burning Ship iteration
    # z = 0
    # z = (|x| + i|y|)^2 + c
    # z = x^2 - y^2 + i(2|x||y|) + c
    
    zx, zy = 0.0, 0.0
    
    for i in range(max_iter):
        # |Re(z)|, |Im(z)|
        zx = abs(zx)
        zy = abs(zy)
        
        # Square
        xtemp = zx*zx - zy*zy + cx
        zy = 2.0 * zx * zy + cy
        zx = xtemp
        
        if zx*zx + zy*zy > 4.0:
            return float(i) / max_iter # Escaped
            
    return 0.0 # Inside

def generate_child_v46(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V46 (The Burning Ship): {output_path}")

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
    # BURNING SHIP GENERATION
    # ---------------------------------------------------------
    
    # Interesting region of Burning Ship:
    # Real: -1.8 to -1.7 (The Ship)
    # Imag: -0.08 to 0.01
    # We want the main "Ship" shape.
    # Main body is roughly around (-1.75, -0.03).
    
    # Let's map the cylinder surface to this complex plane window.
    
    c_real_min = -1.8
    c_real_max = -1.7
    c_imag_min = -0.08
    c_imag_max = 0.02
    
    dr = c_real_max - c_real_min
    di = c_imag_max - c_imag_min
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist
        twist = z_mm * 0.02
        
        # Zoom with height?
        # Map Z to Imaginary axis?
        # Map Theta to Real axis?
        
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
                    # 3. FRACTAL LATTICE
                    
                    # Rotate
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Map to fractal domain
                    theta = math.atan2(y_rot, x_rot)
                    u = (theta + math.pi) / (2.0 * math.pi) # 0 to 1
                    v = z_mm / height # 0 to 1
                    
                    # Repeat pattern 3 times around
                    u_scaled = (u * 3.0) % 1.0
                    
                    # Complex coords
                    cx = c_real_min + u_scaled * dr
                    cy = c_imag_min + v * di
                    
                    val = burning_ship_distance(cx, cy, max_iter=16)
                    
                    # Threshold
                    # Val is 0 (inside) to 1 (fast escape).
                    # Boundary is chaotic.
                    
                    # Create a lattice from the chaotic region
                    # Val around 0.1 to 0.5 is the "coastline".
                    
                    t_min = 0.02
                    t_max = 0.6
                    
                    if val > t_min and val < t_max:
                        # Fractal wall
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Secondary Lattice
                        base_scale = 2.0 * math.pi / 15.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Thicker lattice
                        if abs(g_val) < 0.5:
                            grid[x_idx,y_idx,z_idx] = True
                        # Horizontal Ribs
                        elif z_mm % 25.0 < 2.5:
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
    output_file = os.path.join(output_dir, "child_111_burning_ship.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v46(output_file)
