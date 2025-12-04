import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V21 (Catalog #86): THE JULIA SET (Quaternion Fractal)
# -----------------------------------------------------------------------------
# Concept: A 3D projection of a 4D Julia Set using Quaternions.
#          Z_{n+1} = Z_n^2 + C
#          Where Z and C are quaternions (4 components).
#          We visualize a 3D slice.
# Parents: 81_mandelbrot_zoom (Fractal), 06_quantum_foam (Bubbles).
# -----------------------------------------------------------------------------

def quaternion_julia(x, y, z, max_iter=10):
    # Quaternion Z = x + yi + zj + wk
    # We assume w = 0 for the slice, or map height to w?
    # Let's map z-height to the 'w' component to see evolution?
    # Or just a static 3D slice.
    
    # Constants for C (The parameter that defines the shape)
    # Interesting values: (-0.2, 0.6, 0.0, 0.0) or similar.
    c_r = -0.2
    c_i = 0.6
    c_j = 0.2
    c_k = 0.0
    
    # Z vector
    zx = x
    zy = y
    zz = z
    zw = 0.0 # Slice at w=0
    
    # Iteration
    r = 0.0
    for i in range(max_iter):
        r = math.sqrt(zx*zx + zy*zy + zz*zz + zw*zw)
        if r > 4.0:
            break
        
        # Z^2 for Quaternions
        # (r, i, j, k)^2
        # New r = r^2 - i^2 - j^2 - k^2
        # New i = 2*r*i
        # New j = 2*r*j
        # New k = 2*r*k
        
        nx = zx*zx - zy*zy - zz*zz - zw*zw
        ny = 2*zx*zy
        nz = 2*zx*zz
        nw = 2*zx*zw
        
        zx = nx + c_r
        zy = ny + c_i
        zz = nz + c_j
        zw = nw + c_k
        
    # Distance Estimator (simplified)
    # We return a smoothed iteration count or just the count
    # We want a solid lattice.
    # Boundary is where r approx 2.
    
    # Let's create a "Cloud" density from the potential
    # V = 0.5 * log(r) * r / |dz| ... normal DE is hard without derivative.
    
    # Use smoothed iteration
    if i == max_iter:
        return 0.0 # Inside
        
    return float(i) / max_iter

def generate_child_v21(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V21 (The Julia Set): {output_path}")

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
    
    # Scaling
    # Julia sets are usually in range [-2, 2]
    scale = 3.0 / diameter 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Map Z to fractal space
        z_frac = (z_mm - (height/2)) * scale
        
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
                    # 3. JULIA LATTICE
                    
                    # Fractal Coords
                    x_frac = x_mm * scale
                    y_frac = y_mm * scale
                    
                    # Evaluate
                    val = quaternion_julia(x_frac, y_frac, z_frac)
                    
                    # Threshold
                    # val is 0 (inside) to 1 (outside)
                    # We want the "Boundary" or "Inside"
                    # The inside of a Julia set is often solid.
                    # We want a lattice.
                    
                    # Option A: Intersect with Gyroid (Hybrid)
                    # Option B: Use the "Potential" bands as shells.
                    
                    # Let's try Bands.
                    # val * 10 % 1.0 < t
                    
                    # Or better: Hybrid.
                    # Structure comes from Gyroid, Density comes from Fractal.
                    
                    # Gyroid Backbone
                    base_scale = 2.0 * math.pi / 15.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    # Density: High density near fractal boundary (val approx 0.1 to 0.5)
                    # Low density deep inside (val=0) or far outside (val=1)
                    
                    # Define density mask
                    # We want the "skin" of the fractal
                    density = 0.0
                    if val < 0.5: # Near set
                        density = 1.0 - (val * 2.0) # 1.0 at core, 0 at edge
                        
                    # Thicken Gyroid based on density
                    # Increased base for connectivity
                    t = 0.35 + (density * 0.4)
                    
                    if abs(g_val) < t:
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
    output_file = os.path.join(output_dir, "child_86_julia_set.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v21(output_file)
