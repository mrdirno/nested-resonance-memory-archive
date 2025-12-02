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
# HELIOS LAMP SERIES 05: THE WATER (SHADE)
# -----------------------------------------------------------------------------
# Logic: Fluid Dynamics (Caustics/Ripples).
# Method: Wave interference pattern (Droplets).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE WATER SHADE: {output_path}")
    
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
    
    # Water Logic
    # Interference of circular waves from random points
    # Caustic pattern
    
    num_droplets = 5
    droplets = []
    random.seed(2727)
    
    for _ in range(num_droplets):
        r = random.uniform(0, diameter/2)
        theta = random.uniform(0, 2*math.pi)
        droplets.append((r*math.cos(theta), r*math.sin(theta)))
        
    print("Simulating Fluid Dynamics...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Shape: Slightly bulging droplet shape? Or straight cylinder?
        # Let's do straight cylinder to emphasize surface texture.
        current_radius = radius
        
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

                # --- PRIORITY 3: WATER SHELL ---
                
                if dist_xy > (radius + 5.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Wave calc
                # Sum of sin(dist to droplet)
                
                wave_sum = 0.0
                for drop in droplets:
                    dx, dy = drop
                    # Distance on surface?
                    # Approximate by direct distance
                    d_drop = math.sqrt((x_mm-dx)**2 + (y_mm-dy)**2 + (z_mm*0.5)**2)
                    wave_sum += math.sin(d_drop * 0.3)
                    
                # Normalize
                val = wave_sum / num_droplets
                
                # Surface at radius + val*amplitude
                r_surf = current_radius + val * 5.0
                
                # Thickness
                if abs(dist_xy - r_surf) < (wall_thickness / 2.0):
                    # Smooth surface
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
    output_file = "water_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
