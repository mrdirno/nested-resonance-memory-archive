import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V30 (Catalog #95): THE SCHWARZ LANTERN (Triply Periodic)
# -----------------------------------------------------------------------------
# Concept: A classical Schwarz P (Primitive) surface, but adapted to a
#          cylindrical coordinate system to form a perfect lantern.
#          The cells expand radially.
# Parents: 37_minimal_surface (Topology), 27_gyroid_lattice (Structure).
# Math: cos(r) + cos(theta) + cos(z) = 0 (in warped coords).
# -----------------------------------------------------------------------------

def schwarz_p_cylindrical(x, y, z, radius):
    # Map x,y to r, theta
    r = math.sqrt(x*x + y*y)
    theta = math.atan2(y, x)
    
    # Scale factors
    # Lower radial frequency for robustness
    k_r = 2.0 * math.pi / 40.0
    # Azimuthal frequency (integer for continuity)
    n_theta = 8.0
    # Vertical frequency
    k_z = 2.0 * math.pi / 25.0
    
    val = math.cos(r * k_r) + math.cos(theta * n_theta) + math.cos(z * k_z)
    
    # Add concentric ribs for reinforcement
    val += 0.5 * math.cos(r * k_r * 2.0)
    
    return val

def generate_child_v30(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V30 (The Schwarz Lantern): {output_path}")

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
                    # 3. SCHWARZ LANTERN
                    
                    val = schwarz_p_cylindrical(x_mm, y_mm, z_mm, radius)
                    
                    # Threshold
                    # Increased for connectivity
                    # Thicken at edges to compensate for radial stretching
                    t = 1.0 + (dist_xy / radius) * 0.5
                    
                    # Modulate t to thicken connections
                    t += 0.1 * math.cos(z_mm * 0.1)
                    
                    if abs(val) < t:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                        
                    # Central Hub for structural integrity
                    # Widened hub
                    if dist_xy < 25.0:
                        grid[x_idx,y_idx,z_idx] = True
                        
                    # Bottom Rim for stability
                    if z_mm < 8.0:
                         if dist_xy < radius and dist_xy > (radius - shell_thickness):
                             grid[x_idx,y_idx,z_idx] = True
                        
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
    output_file = os.path.join(output_dir, "child_95_schwarz_lantern.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v30(output_file)