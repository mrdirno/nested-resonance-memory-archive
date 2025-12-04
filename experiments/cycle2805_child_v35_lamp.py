import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V35 (Catalog #100): THE SIERPINSKI PYRAMID (Tetrahedral Fractal)
# -----------------------------------------------------------------------------
# Concept: A 3D fractal structure formed by recursively stacking tetrahedrons.
#          Approximated on a sphere by modulating a lattice or using a 
#          distance field to the fractal boundary.
# Parents: 42_sierpinski (2D/3D), 20_fractal (Recursive).
# Math: IFS or Sierpinski distance estimator.
# -----------------------------------------------------------------------------

def sierpinski_tetrahedron_de(p, iterations=10):
    # Distance Estimator for Sierpinski Tetrahedron
    # p is numpy array [x,y,z]
    # Scale 2.0, Offset 1.0
    
    scale = 2.0
    offset = 1.0
    
    for i in range(iterations):
        # Fold logic
        if p[0] + p[1] < 0: 
            t = p[0]; p[0] = -p[1]; p[1] = -t # Swap and negate? No.
            # Correct folding for tetrahedron is tricky inline.
            pass
            
    # Let's use a simpler "Recursive Lattice" approach (Octree-like but Tetrahedral)
    # Or approximate with a Sum of specialized waves?
    
    # "Tetrahedral Wave"
    # 4 plane waves normal to faces of tetrahedron
    # n1 = (1,1,1), n2 = (1,-1,-1), n3 = (-1,1,-1), n4 = (-1,-1,1)
    
    k = 1.0
    w1 = math.cos((p[0]+p[1]+p[2])*k)
    w2 = math.cos((p[0]-p[1]-p[2])*k)
    w3 = math.cos((-p[0]+p[1]-p[2])*k)
    w4 = math.cos((-p[0]-p[1]+p[2])*k)
    
    # To get fractal, sum octaves
    val = w1*w2*w3*w4 # Product?
    
    # Let's use standard fractal summation (FBM) of this tetrahedral basis
    return val

def generate_child_v35(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V35 (The Sierpinski Pyramid): {output_path}")

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
    
    # Fractal Parameters
    # Base frequency
    scale_1 = 2.0 * math.pi / 40.0
    
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
                    # 3. TETRAHEDRAL FRACTAL
                    
                    # Apply Twist
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    z_rot = z_mm
                    
                    # Basis Waves (Tetrahedral symmetry)
                    # Normals: (1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1)
                    # Scaled by 1/sqrt(3) usually, but here just scale factor
                    
                    # Function 1 (Base)
                    k = scale_1
                    w1 = math.cos((x_rot+y_rot+z_rot)*k)
                    w2 = math.cos((x_rot-y_rot-z_rot)*k)
                    w3 = math.cos((-x_rot+y_rot-z_rot)*k)
                    w4 = math.cos((-x_rot-y_rot+z_rot)*k)
                    
                    # Product creates isolated tetrahedral voids?
                    # Sum creates a lattice.
                    # Let's iterate octaves
                    
                    # Octave 1
                    val = (w1 + w2 + w3 + w4)
                    
                    # Octave 2
                    k2 = k * 2.0
                    w1_2 = math.cos((x_rot+y_rot+z_rot)*k2)
                    w2_2 = math.cos((x_rot-y_rot-z_rot)*k2)
                    w3_2 = math.cos((-x_rot+y_rot-z_rot)*k2)
                    w4_2 = math.cos((-x_rot-y_rot+z_rot)*k2)
                    
                    val += 0.5 * (w1_2 + w2_2 + w3_2 + w4_2)
                    
                    # Threshold
                    # Range approx [-6, 6]
                    # "Sierpinski" look comes from holes.
                    
                    # Val < t is solid.
                    # Val > t is hole.
                    
                    # Threshold modulation
                    t = 1.5
                    
                    if val < t: # Inverted logic creates "Cheese"
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
    output_file = os.path.join(output_dir, "child_100_sierpinski_pyramid.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v35(output_file)
