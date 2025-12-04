import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V6: THE INTERFERENCE WEAVER (Wave Superposition)
# -----------------------------------------------------------------------------
# Concept: A structure born from the collision of multiple invisible wave sources.
#          The "Solid" matter exists only where the waves constructively interfere.
# Parents: 14_swarm (Motion), 26_impossible (Complexity).
# Math: Sum of Sine Waves from distinct point sources.
# -----------------------------------------------------------------------------

def generate_child_v6(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V6 (The Interference Weaver): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 25.0 # Hollow shell thickness
    
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
    # WAVE SOURCES
    # ---------------------------------------------------------
    # We place "Emitters" outside the geometry to push waves through it.
    # Source 1: Top Center
    src1 = np.array([0, 0, height * 1.5])
    # Source 2: Bottom Left
    src2 = np.array([-diameter, -diameter, -height * 0.5])
    # Source 3: Bottom Right
    src3 = np.array([diameter, diameter, -height * 0.5])
    
    # Wavelength (Controls density/scale)
    wavelength = 18.0
    k = 2.0 * math.pi / wavelength
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z for macro shape (Sphere)
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # 1. MOUNTING (Mandatory)
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
                    # 3. INTERFERENCE FIELD
                    p = np.array([x_mm, y_mm, z_mm])
                    
                    d1 = np.linalg.norm(p - src1)
                    d2 = np.linalg.norm(p - src2)
                    d3 = np.linalg.norm(p - src3)
                    
                    # Sum of waves
                    # sin(k*d)
                    val = math.sin(k * d1) + math.sin(k * d2) + math.sin(k * d3)
                    
                    # Range of val is [-3, 3]
                    # We want walls where val is close to 0 (Null zones? No, that's destructive)
                    # Or where val is high (Constructive)?
                    # Let's try iso-surface at 0. This gives the "nodal lines" in 3D.
                    
                    # Variable thickness to create "Breath"
                    # Thicker at bottom, thinner at top
                    base_t = 0.6 # Base thickness
                    
                    if abs(val) < base_t:
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
    output_file = os.path.join(output_dir, "child_v6_interference_weaver.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v6(output_file)
