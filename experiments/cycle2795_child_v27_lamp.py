import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V27 (Catalog #92): THE CLEBSCH SURFACE (Algebraic Geometry)
# -----------------------------------------------------------------------------
# Concept: A visualization of the Clebsch Diagonal Surface.
#          Equation: x^3 + y^3 + z^3 + 1 = (x+y+z+1)^3
#          This surface contains 27 straight lines.
# Parents: 37_minimal_surface (Smooth), 41_calabi_yau (Algebraic).
# Math: Cubic implicit surface.
# -----------------------------------------------------------------------------

def clebsch_surface(x, y, z):
    # Scale coords to range approx [-1, 1]
    # The classic Clebsch is defined in P3 projective space.
    # We use an affine patch or approximation suitable for a lamp.
    
    # Let's use the diagonal cubic form:
    # x^3 + y^3 + z^3 + w^3 = (x+y+z+w)^3
    # Set w = 1.
    # x^3 + y^3 + z^3 + 1 - (x+y+z+1)^3 = 0
    
    w = 1.0
    lhs = x**3 + y**3 + z**3 + w**3
    rhs = (x + y + z + w)**3
    
    val = lhs - rhs
    
    # To make it a lattice, we want a shell around the zero-set.
    # But the Clebsch surface is finite? No, it extends.
    # We need to scale it to fit our sphere.
    
    return val

def generate_child_v27(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V27 (The Clebsch Surface): {output_path}")

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
    # Clebsch interesting features are around origin.
    # Map [-2, 2] to physical size.
    scale = 4.0 / diameter 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Center Z around 0 for algebraic surface
        z_alg = (z_mm - height/2.0) * scale
        
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
                    # 3. CLEBSCH LATTICE
                    
                    # Algebraic coords
                    x_alg = x_mm * scale
                    y_alg = y_mm * scale
                    
                    # Evaluate
                    val = clebsch_surface(x_alg, y_alg, z_alg)
                    
                    # Threshold
                    # We want a shell around the surface.
                    # Since val changes rapidly (cubic), we need a dynamic threshold or normalization.
                    # Approximation: |val| < t
                    
                    # To ensure connectivity and "lattice" look, we intersect with a Gyroid?
                    # Or just use the surface itself which has holes/loops.
                    
                    # The Clebsch surface itself is a smooth manifold. To make it a lattice,
                    # we can boolean intersect it with a Gyroid, OR
                    # Use it as a modulation field for a Gyroid.
                    
                    # Let's make the Surface ITSELF the lamp shade (perforated).
                    # To perforate it, we modulate the thickness with a sine wave?
                    
                    # Perforation Pattern
                    perf = math.sin(x_mm * 0.2) * math.sin(y_mm * 0.2) * math.sin(z_mm * 0.2)
                    
                    # Base Thickness
                    t = 0.5
                    
                    # If perf > 0, we remove the surface (hole)
                    # But we need to keep structure.
                    # Let's just Union Clebsch with Gyroid.
                    
                    # Clebsch Layer
                    is_clebsch = abs(val) < 2.0 # Wide threshold for cubic
                    
                    # Structural Backbone
                    base_scale = 2.0 * math.pi / 20.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    # Increased threshold for connectivity
                    is_gyroid = abs(g_val) < 0.4
                    
                    # Union logic for robustness:
                    # 1. The Clebsch Core (solid surface)
                    # 2. The Clebsch + Gyroid Intersection (lattice aura)
                    
                    # Drastically widened core
                    is_core = abs(val) < 1.5
                    
                    # Central Hub for structural integrity
                    if dist_xy < 20.0:
                        is_core = True
                    
                    if is_core or (is_clebsch and is_gyroid):
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
    output_file = os.path.join(output_dir, "child_92_clebsch_surface.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v27(output_file)
