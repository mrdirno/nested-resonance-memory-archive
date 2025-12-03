import numpy as np
import math
import sys
import struct
import os
import random

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 07: THE ALGORITHM (SHADE)
# -----------------------------------------------------------------------------
# Logic: Sorting Network / Flow Chart.
# Method: Structured diverging paths (Binary Tree or Merge Sort Visualization).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE ALGORITHM SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Algorithm Logic
    # Flow Chart: Nodes diverging and converging.
    # Sorting Network: Vertical lines swapping.
    
    # Let's do a Sorting Network wrapped around the cylinder.
    # N Lines vertical. At intervals, adjacent lines swap.
    
    num_lines = 24
    num_stages = 8
    
    # Define swaps
    swaps = []
    random.seed(101)
    
    stage_h = height / num_stages
    
    for s in range(num_stages):
        # Even/Odd swap pattern
        offset = s % 2
        for i in range(offset, num_lines, 2):
            # Swap i and i+1
            next_i = (i + 1) % num_lines
            swaps.append({
                'z_start': s * stage_h,
                'z_end': (s + 1) * stage_h,
                'idx1': i,
                'idx2': next_i
            })
            
    print("Sorting Data...")
    
    radius = diameter / 2.0
    
    line_thick = 4.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Find current stage
        s_idx = int(z_mm / stage_h)
        if s_idx >= num_stages: s_idx = num_stages - 1
        
        # Progress in stage
        t = (z_mm - (s_idx * stage_h)) / stage_h
        
        # Easing function for swap (Sigmoid)
        ease = 1 / (1 + math.exp(-10 * (t - 0.5)))
        if t < 0.1: ease = 0
        if t > 0.9: ease = 1
        
        # Calculate active line positions
        # Map indices to angles
        
        line_angles = {}
        
        # Default positions
        for i in range(num_lines):
            line_angles[i] = (i / num_lines) * 2 * math.pi
            
        # Apply swaps
        # We need to track current permutation?
        # For visual effect, we just want lines crossing.
        # We don't need persistent state if we just draw the swap locally.
        
        # Current stage swaps
        current_swaps = [sw for sw in swaps if sw['z_start'] <= z_mm < sw['z_end']]
        
        # List of active angle centers
        centers = []
        
        processed_indices = set()
        
        for swap in current_swaps:
            i1 = swap['idx1']
            i2 = swap['idx2']
            
            a1 = (i1 / num_lines) * 2 * math.pi
            a2 = (i2 / num_lines) * 2 * math.pi
            
            # Handle wrap around
            if abs(a1 - a2) > math.pi:
                if a1 < a2: a1 += 2*math.pi
                else: a2 += 2*math.pi
            
            # Interpolate
            # Line 1 goes a1 -> a2
            # Line 2 goes a2 -> a1
            
            curr_a1 = a1 + (a2 - a1) * ease
            curr_a2 = a2 + (a1 - a2) * ease
            
            centers.append(curr_a1)
            centers.append(curr_a2)
            
            processed_indices.add(i1)
            processed_indices.add(i2)
            
        # Add non-swapping lines
        for i in range(num_lines):
            if i not in processed_indices:
                centers.append((i / num_lines) * 2 * math.pi)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                if angle < 0: angle += 2*math.pi
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: ALGORITHM SHELL (Anisotropic) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Sorting Network Pattern (Anisotropic - Vertical Flow)
                
                is_solid = False
                
                for c in centers:
                    # Angular distance
                    diff = abs(angle - c)
                    # Wrap check
                    if diff > math.pi: diff = 2*math.pi - diff
                    
                    # Convert to arc length
                    arc_len = diff * dist_xy
                    
                    if arc_len < (line_thick / 2.0):
                        is_solid = True
                        break
                        
                # Horizontal connectors at stage boundaries
                # Anisotropy: Connectors get further apart at top (Efficiency)
                # stage_h is constant, but we can filter
                
                stage_local = int(z_mm / stage_h)
                if stage_local % 2 == 0: # Only even stages have connectors
                    if abs(z_mm % stage_h) < 2.0:
                        is_solid = True
                    
                # Hand access override
                if dist_xy < hand_access_radius: is_solid = False
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "algorithm_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
