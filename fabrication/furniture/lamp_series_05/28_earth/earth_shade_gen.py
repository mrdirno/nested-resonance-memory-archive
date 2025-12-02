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
# HELIOS LAMP SERIES 05: THE EARTH (SHADE)
# -----------------------------------------------------------------------------
# Logic: Erosion / Strata (Geological Layers).
# Method: Horizontal layers modulated by noise (Canyon walls).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE EARTH SHADE: {output_path}")
    
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
    
    # Erosion Logic
    # 1. Stratified Noise (Strong Z dependence)
    # 2. Vertical Erosion (drip lines)
    
    scale_strata = 2.0 * math.pi / 10.0 # Layers
    scale_erosion = 2.0 * math.pi / 40.0 # Large features
    
    print("Simulating Erosion...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SPIDER FITTER ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: EARTH SHELL ---
                
                if dist_xy > (radius + 10.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness - 10.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Strata Noise
                # sin(z * freq + noise(x,y))
                
                # Low freq horizontal displacement
                warp_x = 10.0 * math.sin(x_mm * 0.05)
                warp_y = 10.0 * math.sin(y_mm * 0.05)
                
                strata = math.sin((z_mm + warp_x + warp_y) * 0.2) 
                
                # Erosion (Cuts into the strata)
                # Vertical ridges
                erosion = math.sin(x_mm * 0.15) * math.sin(y_mm * 0.15)
                
                # Combine
                # Radius modulation
                # Base radius - erosion depth
                
                r_surf = radius + 5.0 * strata - 10.0 * abs(erosion)
                
                # Wall thickness variation
                # Inner wall also eroded?
                # Or smooth? Let's make inner smooth for access.
                
                if dist_xy <= r_surf and dist_xy >= (r_surf - wall_thickness):
                    # Add cracks?
                    # High freq noise check
                    crack = math.sin(x_mm*0.8)*math.sin(y_mm*0.8)*math.sin(z_mm*0.8)
                    if crack > 0.8:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False
                    
                # Ensure Hand Access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "earth_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
