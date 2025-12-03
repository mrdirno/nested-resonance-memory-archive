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
# HELIOS LAMP SERIES 05: THE CHAOS (SHADE)
# -----------------------------------------------------------------------------
# Logic: Entropy / Butterfly Effect.
# Method: Strange Attractor Trajectory (Lorenz/Rossler) or heavily distorted noise.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE CHAOS SHADE: {output_path}")
    
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
    
    # Chaos Logic
    # Lorenz Attractor Trail mapped to surface?
    # Or noise field that is highly turbulent.
    
    # Let's use "Curl Noise" or simply heavily warped domain
    # warp = noise(p)
    # val = noise(p + warp)
    
    # Deterministic chaos:
    # z_twist = sin(z * k1)
    # r_warp = sin(theta * k2 + z_twist)
    
    scale = 2.0 * math.pi / 40.0
    
    print("Increasing Entropy...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
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

                # --- PRIORITY 3: CHAOS SHELL (Anisotropic) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Chaotic Pattern (Anisotropic Flow)
                # Domain Warping
                
                # Warp vector (Anisotropic)
                # Stronger Z-Warp
                wx = 25.0 * math.sin(y_mm * 0.05 + z_mm * 0.02)
                wy = 25.0 * math.cos(x_mm * 0.05 - z_mm * 0.02)
                wz = 10.0 * math.sin(x_mm * 0.04 + y_mm * 0.04)
                
                # Sample point
                sx = x_mm + wx
                sy = y_mm + wy
                sz = z_mm + wz
                
                # Pattern function: Sine summation
                # Z-Stretched Pattern
                val = math.sin(sx * scale) + math.sin(sy * scale) + math.sin(sz * scale * 0.5)
                
                if abs(val) < 0.6: # Thicker strands
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "chaos_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
