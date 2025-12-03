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
# HELIOS LAMP SERIES 04: THE GLITCH (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Signal Noise (Broken Column).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating GLITCH SHAFT: {output_path}")
    
    base_width = 30.0 # Square shaft
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_width + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Glitch Logic
    # Segments shifted in X/Y
    random.seed(500)
    
    segments = []
    current_z = 0.0
    while current_z < height:
        h = random.uniform(5.0, 20.0)
        ox = random.uniform(-5.0, 5.0)
        oy = random.uniform(-5.0, 5.0)
        if random.random() > 0.8: # Occasional alignment
            ox = 0
            oy = 0
        segments.append({'h': h, 'ox': ox, 'oy': oy})
        current_z += h
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Find segment
        seg_z = 0.0
        active_seg = segments[0]
        for s in segments:
            seg_z += s['h']
            if z_mm < seg_z:
                active_seg = s
                break
        
        ox = active_seg['ox']
        oy = active_seg['oy']
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 QA Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    # Base square centered
                    if abs(x_mm) < (base_width/2) and abs(y_mm) < (base_width/2):
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Shifted Square (Anisotropic Shear)
                sx = x_mm - ox
                sy = y_mm - oy
                
                if abs(sx) < (base_width/2) and abs(sy) < (base_width/2):
                    # Noise Cutouts (Anisotropic Z-Streaks)
                    # Missing scanlines
                    
                    is_noise = False
                    if (z_mm % 10.0) < 1.0: # Missing slice every 10mm
                        if random.random() > 0.5: is_noise = True
                        
                    if is_noise:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "glitch_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
