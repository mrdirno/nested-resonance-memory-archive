import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V13: THE VOID MANIFOLD (Boolean Subtraction)
# -----------------------------------------------------------------------------
# Concept: A solid block that has been carved away by multiple invisible forces.
#          The "Lattice" is the negative space of a swarm of spheres or pipes.
# Parents: 03_singularity (Void), 06_quantum_foam (Bubbles).
# Math: Solid - Union( Shapes )
# -----------------------------------------------------------------------------

def generate_child_v13(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V13 (The Void Manifold): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 30.0 # Thick shell to be carved
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # Void Generators
    # We define a list of "Void Objects" (spheres, capsules) that subtract from the solid.
    # Here we use a procedural approach: A spiral of voids.
    
    void_centers = []
    num_voids = 60
    for i in range(num_voids):
        t = i / num_voids
        # Spiral path
        angle = t * math.pi * 8.0 # 4 turns
        r_path = radius * 0.8 * (1.0 - t*0.5)
        z_path = height * t
        
        x_c = r_path * math.cos(angle)
        y_c = r_path * math.sin(angle)
        z_c = z_path
        
        # Void radius varies
        r_void = 15.0 + 10.0 * math.sin(t * math.pi * 4.0)
        
        void_centers.append((x_c, y_c, z_c, r_void))
        
    # Secondary Voids: Vertical Channels
    vertical_voids = []
    num_vertical = 8
    for i in range(num_vertical):
        angle = (i / num_vertical) * 2.0 * math.pi
        r_v = radius * 0.5
        x_v = r_v * math.cos(angle)
        y_v = r_v * math.sin(angle)
        vertical_voids.append((x_v, y_v))

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z for macro sphere
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
                
                # 2. SHELL (The Canvas)
                # Base state is SOLID shell
                if z_mm < 4.0:
                    hand_radius = radius - shell_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                is_solid = False
                if in_outer and not in_inner and not in_hand_zone:
                    is_solid = True
                    
                    # 3. SUBTRACTIVE GEOMETRY
                    
                    # Check Spiral Voids
                    for vx, vy, vz, vr in void_centers:
                        d_void = math.sqrt((x_mm - vx)**2 + (y_mm - vy)**2 + (z_mm - vz)**2)
                        if d_void < vr:
                            is_solid = False
                            break
                    
                    if not is_solid:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # Check Vertical Voids (Cylinders)
                    # Slight twist to make them interesting
                    twist_angle = z_mm * 0.01
                    x_rot = x_mm * math.cos(twist_angle) - y_mm * math.sin(twist_angle)
                    y_rot = x_mm * math.sin(twist_angle) + y_mm * math.cos(twist_angle)
                    
                    for vx, vy in vertical_voids:
                        d_cyl = math.sqrt((x_rot - vx)**2 + (y_rot - vy)**2)
                        if d_cyl < 8.0: # 16mm diameter channels
                            is_solid = False
                            break
                            
                    grid[x_idx,y_idx,z_idx] = is_solid
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
    output_file = os.path.join(output_dir, "child_v13_void_manifold.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v13(output_file)
