import numpy as np
import math
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V22 (Catalog #87): THE VORONOI FOAM (Minimal Surfaces)
# -----------------------------------------------------------------------------
# Concept: A lattice based on 3D Voronoi cells that have been "relaxed" 
#          (Lloyd's Algorithm) to approach minimal surface area.
#          Similar to soap bubbles or trabecular bone.
# Parents: 19_voronoi (Base), 30_kelvin_foam (Optimization).
# Math: 3D Distance Field to nearest N points.
# -----------------------------------------------------------------------------

def generate_child_v22(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V22 (The Voronoi Foam): {output_path}")

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
    # VORONOI SEED GENERATION
    # ---------------------------------------------------------
    # We want a regular-ish distribution but organic.
    # Poisson Disk sampling or Jittered Grid.
    
    # Using Jittered Grid for efficiency/coverage
    cell_size = 25.0
    grid_cells_x = int(diameter / cell_size) + 2
    grid_cells_y = int(diameter / cell_size) + 2
    grid_cells_z = int(height / cell_size) + 2
    
    seeds = []
    
    for gx in range(grid_cells_x):
        for gy in range(grid_cells_y):
            for gz in range(grid_cells_z):
                # Base position
                bx = (gx * cell_size) - radius - (cell_size/2)
                by = (gy * cell_size) - radius - (cell_size/2)
                bz = (gz * cell_size)
                
                # Jitter
                jx = bx + random.uniform(0, cell_size)
                jy = by + random.uniform(0, cell_size)
                jz = bz + random.uniform(0, cell_size)
                
                seeds.append((jx, jy, jz))
                
    # Optimization: KD-Tree or simply iterate if N is small.
    # N ~ 8*8*6 = 384. Small enough for brute force per voxel?
    # 1M voxels * 384 checks = 384M ops. Python might choke.
    # We need to optimize.
    
    # Optimized Voronoi: Iterate Voxels, only check local seeds?
    # Or Iterate Seeds and "paint" distance field?
    
    # Let's use a "Cell Noise" approach (Worley Noise) 
    # which is effectively implicit Voronoi on a grid.
    # We implement a custom 3D Worley noise function.
    
    # Helper: Fast 3D Worley
    # But we need "Edges" (F2 - F1).
    
    # Actually, for a lamp, we want thick struts.
    # F2 - F1 < Thickness gives edges.
    
    # Let's stick to the implicit grid traversal but optimize.
    # We only need to check neighbors.
    
    # Simpler approach: Periodic Voronoi (Cell Noise).
    # Map p to integer lattice + offset.
    
    pass # Placeholder for inner logic structure

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
                    # 3. VORONOI FOAM
                    
                    # Worley Noise Implementation (Inline)
                    # Cell ID
                    scale = 0.06 # controls cell size
                    
                    px = x_mm * scale
                    py = y_mm * scale
                    pz = z_mm * scale
                    
                    ix = math.floor(px)
                    iy = math.floor(py)
                    iz = math.floor(pz)
                    
                    fx = px - ix
                    fy = py - iy
                    fz = pz - iz
                    
                    min_dist = 100.0
                    second_min_dist = 100.0
                    
                    # Check 3x3x3 neighbors
                    for k in range(-1, 2):
                        for j in range(-1, 2):
                            for i in range(-1, 2):
                                # Hash for random point in neighbor cell
                                # Simple pseudo-random
                                n_ix = ix + i
                                n_iy = iy + j
                                n_iz = iz + k
                                
                                # Hash
                                seed = (n_ix * 73856093) ^ (n_iy * 19349663) ^ (n_iz * 83492791)
                                seed = (seed * seed) * 12345
                                
                                # Random position in cell (0 to 1)
                                rx = ((seed & 1023) / 1024.0)
                                ry = (((seed >> 10) & 1023) / 1024.0)
                                rz = (((seed >> 20) & 1023) / 1024.0)
                                
                                # Vector from current point to neighbor feature point
                                dx = (i + rx) - fx
                                dy = (j + ry) - fy
                                dz = (k + rz) - fz
                                
                                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                                
                                if d < min_dist:
                                    second_min_dist = min_dist
                                    min_dist = d
                                elif d < second_min_dist:
                                    second_min_dist = d
                    
                    # Edge Distance = F2 - F1
                    edge_dist = second_min_dist - min_dist
                    
                    # Threshold
                    # We want edges -> Thick lattice
                    # Edge distance is 0 at the exact boundary (Voronoi face).
                    # We want solid where edge_dist < thickness
                    
                    thickness = 0.15 # Base thickness in feature space
                    
                    # Modulate thickness with height (Breath)
                    thickness += 0.05 * math.sin(z_mm * 0.05)
                    
                    if edge_dist < thickness:
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
    output_file = os.path.join(output_dir, "child_87_voronoi_foam.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v22(output_file)
