import numpy as np
import math
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V44 (Catalog #109): THE MORAN PROCESS (Stochastic Growth)
# -----------------------------------------------------------------------------
# Concept: A 3D visualization of a stochastic evolutionary process (Moran Process).
#          Cells (voxels) reproduce and replace neighbors based on fitness.
#          We simulate this on a grid to create an organic, competitive growth structure.
# Parents: 130_game_of_life (Cellular Automata), 74_biomorphic_turing (Biological).
# Math: Stochastic Matrix / Birth-Death Process.
# -----------------------------------------------------------------------------

def generate_child_v44(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V44 (The Moran Process): {output_path}")

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
    # MORAN SIMULATION
    # ---------------------------------------------------------
    
    # We use a coarse grid for the simulation, then upscale.
    coarse_scale = 6.0 # 6mm voxels
    
    cx_dim = int(diameter / coarse_scale) + 4
    cy_dim = int(diameter / coarse_scale) + 4
    cz_dim = int(height / coarse_scale) + 4
    
    # Population types: 0 (Empty), 1 (Type A - Structural), 2 (Type B - Void/Eater)
    # Actually, let's just grow Type A against Empty.
    
    population = np.zeros((cx_dim, cy_dim, cz_dim), dtype=int)
    
    # Initialize: Seed Type A at bottom ring
    center_x = cx_dim // 2
    center_y = cy_dim // 2
    
    for x in range(cx_dim):
        for y in range(cy_dim):
            dx = (x - center_x) * coarse_scale
            dy = (y - center_y) * coarse_scale
            d = math.sqrt(dx*dx + dy*dy)
            
            # Seed ring
            if d < radius and d > radius * 0.5:
                population[x, y, 1] = 1
                
    # Simulation Steps
    steps = 55
    
    for s in range(steps):
        new_pop = population.copy()
        
        # Iterate active cells
        active_indices = np.argwhere(population == 1)
        
        if len(active_indices) == 0: break
        
        # Random shuffle to simulate stochasticity
        np.random.shuffle(active_indices)
        
        for x, y, z in active_indices:
            # Check neighbors
            # 6-neighborhood
            neighbors = [
                (x+1, y, z), (x-1, y, z),
                (x, y+1, z), (x, y-1, z),
                (x, y, z+1), (x, y, z-1)
            ]
            
            # Birth
            for nx, ny, nz in neighbors:
                if 0 <= nx < cx_dim and 0 <= ny < cy_dim and 0 <= nz < cz_dim:
                    # If empty, reproduce with probability p_birth
                    if population[nx, ny, nz] == 0:
                        
                        # Bias growth UP and IN
                        bias = 1.5 # Increased bias
                        if nz > z: bias *= 2.0 # Grow up strongly
                        
                        # Distance from center bias
                        ndx = (nx - center_x) * coarse_scale
                        ndy = (ny - center_y) * coarse_scale
                        ndist = math.sqrt(ndx*ndx + ndy*ndy)
                        
                        # Simple biased random walk
                        if random.random() < 0.4 * bias: # Increased prob
                            new_pop[nx, ny, nz] = 1
            
        population = new_pop
        
    # Upscale to fine grid
    print("Upscaling Moran Structure...")
    
    # Safety Net Lattice
    # To ensure connectivity of isolated growth clusters
    for z_idx in range(res_z):
        z_mm = z_idx * step
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                # Only inside shell
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                if dist_xy > radius: continue
                
                # Gyroid Safety Net
                base_scale = 2.0 * math.pi / 25.0
                g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                        np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                        np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                if abs(g_val) < 0.50:
                    grid[x_idx, y_idx, z_idx] = True

    for x in range(cx_dim):
        for y in range(cy_dim):
            for z in range(cz_dim):
                if population[x, y, z] == 1:
                    
                    # Map coarse voxel to fine grid range
                    z_start_mm = z * coarse_scale
                    x_start_mm = (x - center_x) * coarse_scale
                    y_start_mm = (y - center_y) * coarse_scale
                    
                    # Convert to fine indices (approx)
                    gz_start = int(z_start_mm / step)
                    gx_start = int((x_start_mm + radius) / step)
                    gy_start = int((y_start_mm + radius) / step)
                    
                    steps_coarse = int(coarse_scale / step)
                    
                    for k in range(steps_coarse):
                        iz = gz_start + k
                        if iz >= res_z: continue
                        z_mm = iz * step
                        
                        for i in range(steps_coarse):
                            ix = gx_start + i
                            if ix < 0 or ix >= res_x: continue
                            x_mm = (ix * step) - radius
                            
                            for j in range(steps_coarse):
                                iy = gy_start + j
                                if iy < 0 or iy >= res_y: continue
                                y_mm = (iy * step) - radius
                                
                                # Check sphere bounds
                                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                                effective_z = z_mm
                                if z_mm > (height - 10.0): effective_z = height - 10.0
                                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                                dist_spherical = math.sqrt(dist_sq)
                                
                                in_outer = dist_spherical <= radius
                                in_inner = dist_spherical < (radius - shell_thickness)
                                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                                
                                if in_outer and not in_inner and not in_hand_zone:
                                    # Gyroid Intersection
                                    base_scale = 2.0 * math.pi / 12.0
                                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                                            
                                    # Thicker blocks
                                    if abs(g_val) < 0.75:
                                        grid[ix, iy, iz] = True

    # 1. MOUNTING
    print("Applying Mounting...")
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
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                cap = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap is not None:
                    grid[x_idx,y_idx,z_idx] = cap
                    continue
                    
                spider = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider is not None:
                    grid[x_idx,y_idx,z_idx] = spider
                    
                # Ensure connectivity of random growth
                if dist_xy < 15.0 and z_mm > 10.0:
                    # Lattice column
                    base_scale = 2.0 * math.pi / 15.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    if abs(g_val) < 0.25:
                        grid[x_idx,y_idx,z_idx] = True

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_109_moran_process.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v44(output_file)