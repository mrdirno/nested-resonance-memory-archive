import numpy as np
import math
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V17: THE LIGHTNING BOLT (Diffusion Limited Aggregation)
# -----------------------------------------------------------------------------
# Concept: A branching structure resembling a lightning strike or Lichtenberg figure.
#          The lattice is formed by the union of many jagged paths originating
#          from the top and grounding at the bottom.
# Parents: 17_lightning_bolt (DLA), 13_pulsar_beam (Energy).
# Math: Random Walk / L-System Skeleton -> Voxelized.
# -----------------------------------------------------------------------------

def generate_child_v17(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V17 (The Lightning Bolt): {output_path}")

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
    # LIGHTNING GENERATION (Procedural Skeleton)
    # ---------------------------------------------------------
    
    # Define "Main Branches"
    # Start at top center, branch out towards bottom rim
    
    root = (0, 0, height)
    branches = []
    
    # Number of main bolts
    num_bolts = 12
    
    for i in range(num_bolts):
        angle = (i / num_bolts) * 2.0 * math.pi
        # Target somewhat random points on the sphere surface
        target_r = radius * 0.9
        target_x = target_r * math.cos(angle)
        target_y = target_r * math.sin(angle)
        target_z = height * 0.2 # Near bottom
        
        # Generate jagged path from root to target
        current = np.array(root)
        target = np.array([target_x, target_y, target_z])
        
        # Number of segments
        segments = 25
        
        path = [current]
        
        for j in range(segments):
            # Vector to target
            diff = target - current
            dist = np.linalg.norm(diff)
            if dist < step:
                break
                
            # Normalized direction
            direction = diff / dist
            
            # Add randomness (Jitter)
            # The "Jaggedness" factor
            jitter = np.random.uniform(-1, 1, 3)
            # Project jitter to be somewhat perpendicular to direction?
            # Or just raw noise
            
            # Step size
            step_len = (dist / (segments - j)) 
            
            next_pos = current + direction * step_len + jitter * 8.0
            
            # Constrain to sphere?
            # We want it inside the shell.
            # Let's just let it be geometric lightning first, then crop.
            
            path.append(next_pos)
            current = next_pos
            
            # Branching?
            if random.random() < 0.15 and j < segments - 5:
                # Create a small side branch
                branch_dir = direction + np.random.uniform(-1, 1, 3)
                branch_end = current + branch_dir * 30.0
                branches.append([current, branch_end]) # Store segment
                
        # Add main path segments
        for k in range(len(path)-1):
            branches.append([path[k], path[k+1]])

    # ---------------------------------------------------------
    # RASTERIZATION
    # ---------------------------------------------------------
    # Convert segments to Voxel Grid (Line Drawing)
    
    # Thickness of bolts
    bolt_radius = 3.0 # 6mm thick lines
    
    # Helper: Point to Line Segment Distance
    def dist_to_segment(p, a, b):
        # p, a, b are numpy arrays
        ab = b - a
        ap = p - a
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0.0, min(1.0, t))
        closest = a + t * ab
        return np.linalg.norm(p - closest)

    # Optimize: Bounding box check for each segment? 
    # Or iterate grid and check distance to all segments? (Slow)
    # Faster: Draw segments into grid.
    
    # Iterate through grid points is safest for complex boolean logic.
    # To speed up, we can filter by macro shell first.
    
    # Pre-compute segments as arrays
    seg_starts = np.array([b[0] for b in branches])
    seg_ends = np.array([b[1] for b in branches])
    seg_vecs = seg_ends - seg_starts
    seg_lens_sq = np.sum(seg_vecs**2, axis=1)
    
    # This is O(N_voxels * N_segments).
    # N_voxels ~ 1M. N_segments ~ 300. 300M ops. Python might be slow.
    # Let's try to define a Distance Field Function?
    
    # Alternative: Use a Lattice that "looks" like lightning?
    # Diffusion Limited Aggregation (DLA) simulation?
    # Or... "Ridged Noise" (Voronoi Edges or Perlin ridges).
    
    # Let's use 3D Ridged Noise (Lightning/Veins)
    # `1.0 - abs(noise)` gives sharp ridges.
    
    def lightning_noise(x, y, z):
        # Simple multi-octave ridged noise
        # Base
        n1 = math.sin(x*0.1)*math.cos(y*0.13) + math.sin(z*0.1 + x*0.05)
        # Detail
        n2 = math.sin(x*0.3)*math.cos(y*0.35) + math.sin(z*0.32)
        
        # Ridge
        val = 1.0 - abs(n1 + n2 * 0.5)
        return val

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
                    # 3. LIGHTNING FIELD
                    # Use ridged noise instead of explicit segments for speed/robustness
                    
                    # Twist the noise for flow
                    twist = z_mm * 0.02
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    l_val = lightning_noise(x_rot, y_rot, z_mm)
                    
                    # Threshold
                    # Thicken veins
                    t = 0.5
                    is_lightning = l_val > t
                    
                    # Backup Lattice (Scaffold)
                    # Ensure connectivity
                    base_scale = 2.0 * math.pi / 20.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    is_scaffold = abs(g_val) < 0.7 # Thicker scaffold
                    
                    if is_lightning or is_scaffold:
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
    output_file = os.path.join(output_dir, "child_v17_lightning_bolt.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v17(output_file)
