import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V16: THE MANDELBROT ZOOM (Complex Dynamics)
# -----------------------------------------------------------------------------
# Concept: A 3D lamp shade where the surface topography is defined by the
#          escape time of the Mandelbrot set.
# Parents: 16_mandelbrot_zoom (2D Fractal), 27_gyroid_lattice (Base).
# Math: z_{n+1} = z_n^2 + c in 3D via Quaternion or iterative mapping.
#       We use "Mandelbulb" power 2 or just extruded Mandelbrot heightmap.
# -----------------------------------------------------------------------------

def mandelbrot_potential(x, y, z, max_iter=12):
    # We map 3D coordinates to Complex plane + Z modulation
    # c = (x + iy)
    # But we want a 3D structure.
    # Let's use a rotationally symmetric Mandelbrot "Bulb" approximation
    # or simply map the escape time to lattice density.
    
    # Map spatial (x,y) to complex plane c
    # Center is roughly (-0.5, 0)
    scale = 2.0 / 100.0 # Fit 200mm into [-2, 2]
    
    cx = x * scale - 0.5
    cy = y * scale
    
    # Z affects the "Zoom" or the "Power" or simply cross section?
    # Let's make Z affect the 'c' value slightly to twist the fractal.
    
    cx += math.sin(z * 0.05) * 0.2
    cy += math.cos(z * 0.05) * 0.2
    
    c = complex(cx, cy)
    z_val = 0j
    
    iter_count = 0
    for i in range(max_iter):
        if abs(z_val) > 2.0:
            break
        z_val = z_val * z_val + c
        iter_count += 1
        
    # Return value: 0 (inside) to 1 (outside fast)
    # Inside set -> High iteration -> Solid?
    # Boundary is most interesting.
    
    # Let's create a lattice where density = iteration count
    # Smoothed iteration count
    
    if iter_count == max_iter:
        return 1.0 # Deep inside set
        
    # Smooth coloring renormalization
    log_zn = math.log(abs(z_val))
    nu = math.log(log_zn / math.log(2.0)) / math.log(2.0)
    res = (iter_count + 1 - nu) / max_iter
    return res

def generate_child_v16(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V16 (The Mandelbrot Zoom): {output_path}")

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
                    
                    # Get Mandelbrot potential (0 to 1)
                    m_val = mandelbrot_potential(x_mm, y_mm, z_mm)
                    
                    # We combine this with a structural lattice (Gyroid)
                    # The fractal defines the *density* of the Gyroid.
                    # High M_val (Boundary) -> Dense
                    # Low M_val (Outside) -> Sparse
                    
                    # Gyroid
                    base_scale = 2.0 * math.pi / 12.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                            
                    # Threshold modulation
                    # Standard Wall: |g| < t
                    # We want t to be high where m_val is interesting (0.3 to 0.7)
                    # and low elsewhere?
                    
                    # Actually, let's just use M_val as a boolean mask on the Gyroid?
                    # Or create a "Mandelbrot Skin".
                    
                    # Let's map M_val directly to solid/void for a pure fractal look,
                    # but ensure connectivity by Union with thin Gyroid.
                    
                    # Fractal shell
                    # Expanded range for solidity
                    is_fractal_solid = (m_val > 0.1) and (m_val < 0.6) 
                    
                    # Lattice backbone
                    # Thickened for connectivity
                    is_lattice = abs(g_val) < 0.4
                    
                    if is_fractal_solid or is_lattice:
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
    output_file = os.path.join(output_dir, "child_v16_mandelbrot_zoom.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v16(output_file)
