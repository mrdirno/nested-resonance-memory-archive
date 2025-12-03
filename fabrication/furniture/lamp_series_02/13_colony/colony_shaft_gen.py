import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE COLONY (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Jagged Lightning Path, Library Integration.
# Logic: Lightning Bolt / Lichtenberg Figure.
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating COLONY SHAFT (v2.0): {output_path}")
    
    base_radius = 25.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Lightning Logic (v2.0: More jagged)
    # Jagged path along Z
    # r(z) offset by noise
    
    import random
    random.seed(777)
    
    # Generate jagged path
    path_points = []
    num_segments = 15 # Increased segments for jaggedness
    cx, cy = 0.0, 0.0
    
    for i in range(num_segments + 1):
        z = (i / num_segments) * height
        # Random walk
        cx += random.uniform(-8, 8)
        cy += random.uniform(-8, 8)
        # constrain
        if abs(cx) > 12: cx *= 0.6
        if abs(cy) > 12: cy *= 0.6
        path_points.append((cx, cy, z))
        
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Interpolate Path
        # Find segment
        segment_h = height / num_segments
        seg_idx = min(int(z_mm / segment_h), num_segments - 1)
        t = (z_mm - (seg_idx * segment_h)) / segment_h
        
        p1 = path_points[seg_idx]
        p2 = path_points[seg_idx+1]
        
        # Lerp
        path_x = p1[0] + (p2[0] - p1[0]) * t
        path_y = p1[1] + (p2[1] - p1[1]) * t
        
        # Lightning Thickness
        # Varies sharply
        l_thick = 8.0 + 3.0 * math.sin(z_mm * 0.5)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist_origin = math.sqrt(x_mm**2 + y_mm**2)
                dist_path = math.sqrt((x_mm-path_x)**2 + (y_mm-path_y)**2)
                
                # V4 Core
                if dist_origin < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist_origin < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist_origin < base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Lightning Structure
                if dist_path < l_thick:
                    # Add jagged noise to surface (Anisotropic - Stretched Z)
                    noise = math.sin(x_mm) * math.sin(y_mm) * math.sin(z_mm * 0.5) # Stretch Z
                    if noise > -0.5: # Craggy
                        grid[x_idx,y_idx,z_idx] = True

    # Clean Dust
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "colony_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
