import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V23 (Catalog #88): THE WEAIRE-PHELAN 2 (Optimal Foam)
# -----------------------------------------------------------------------------
# Concept: The structure of the Beijing Water Cube.
#          A specific configuration of Kelvin cells (Tetrakaidecahedra) and 
#          Pyritohedra that fills space with less surface area than Kelvin's foam.
# Parents: 33_weaire_phelan (Gen 11), 30_kelvin_foam (Gen 10).
# Math: Approximated by the A15 Crystallographic Phase (Beta-Tungsten).
#       Implicit form: cos(x)cos(y) + cos(y)cos(z) + cos(z)cos(x) ... etc.
# -----------------------------------------------------------------------------

def weaire_phelan_approx(x, y, z):
    # The A15 phase is a good approximation for the WP structure's topology.
    # Symmetries of Pm3n space group.
    
    # Formula from "Level Set Method for Microstructure Design"
    # Or simpler approximation:
    # 4 * (cos(x)*cos(y) + cos(y)*cos(z) + cos(z)*cos(x)) - 3 * cos(x)*cos(y)*cos(z) + ...
    
    # Let's use a known implicit approximation for A15:
    # cos(x)*cos(y) + cos(y)*cos(z) + cos(z)*cos(x) - 0.6 = 0? No that's P surface-ish.
    
    # Better approximation for A15 (Beta-W):
    # 2.0 * (cos(x)*cos(y) + cos(y)*cos(z) + cos(z)*cos(x)) - (cos(2*x) + cos(2*y) + cos(2*z))
    
    cx = math.cos(x)
    cy = math.cos(y)
    cz = math.cos(z)
    
    # Primary term (BCC-like)
    term1 = cx*cy + cy*cz + cz*cx
    
    # Secondary term (Modulation)
    c2x = math.cos(2.0 * x)
    c2y = math.cos(2.0 * y)
    c2z = math.cos(2.0 * z)
    
    term2 = c2x + c2y + c2z
    
    # Combined
    # Coefficients tuned for aesthetic "Bubble" packing
    val = 2.0 * term1 - 0.5 * term2
    
    return val

def generate_child_v23(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V23 (The Weaire-Phelan 2): {output_path}")

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
    
    # Scale for the Foam
    base_scale = 2.0 * math.pi / 30.0 # Large bubbles
    
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
                    # 3. WEAIRE-PHELAN FOAM
                    
                    # Evaluate A15 Structure
                    val = weaire_phelan_approx(x_mm * base_scale, y_mm * base_scale, z_mm * base_scale)
                    
                    # Threshold
                    # We want the walls between bubbles.
                    # The implicit function creates "Blobs" at high values.
                    # We want the "Interstices" or a thick Iso-surface.
                    
                    # Let's use a band threshold to create hollow shells (bubbles).
                    # Or a simple wall threshold.
                    
                    # Val range ~ [-3, 5]
                    
                    # Experimentally, walls are near 0?
                    # If we treat > 0 as solid, we get solid A15 lattice.
                    
                    # Let's modulate the wall thickness.
                    t = 0.5
                    
                    if abs(val) < t:
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
    output_file = os.path.join(output_dir, "child_88_weaire_phelan_2.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v23(output_file)
