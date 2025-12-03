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
# HELIOS LAMP SERIES 04: THE GLITCH (SHADE)
# -----------------------------------------------------------------------------
# Logic: Digital Artifact (Datamosh).
# Method: Voxel Displacement / Horizontal Banding.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE GLITCH SHADE: {output_path}")
    
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
    
    # Glitch Logic
    # 1. Define horizontal bands of varying height
    # 2. Each band has a random X/Y offset (Datamosh)
    # 3. Add pixel noise (missing blocks)
    
    random.seed(9000)
    
    # Pre-compute bands
    bands = []
    current_z = 0.0
    while current_z < height:
        h = random.uniform(2.0, 15.0) # Band height
        # Displacement vector
        dx = random.uniform(-10.0, 10.0)
        dy = random.uniform(-10.0, 10.0)
        
        # Glitch probability
        if random.random() > 0.7: # 30% chance of major glitch
            dx *= 3.0
            dy *= 3.0
            
        bands.append({'h': h, 'dx': dx, 'dy': dy})
        current_z += h
        
    print("Corrupting Data...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Determine current band
        band_z = 0.0
        active_band = bands[0]
        for b in bands:
            band_z += b['h']
            if z_mm < band_z:
                active_band = b
                break
        
        dx = active_band['dx']
        dy = active_band['dy']
        
        # Voxelize effect: Quantize z?
        # No, keep z continuous for printing, but xy shift is sharp
        
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

                # --- PRIORITY 3: GLITCH SHELL (Anisotropic) ---
                
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Shift coordinates for shell
                x_shifted = x_mm - dx
                y_shifted = y_mm - dy
                
                dist_shifted = math.sqrt(x_shifted**2 + y_shifted**2)
                
                # Shell logic on shifted coords
                is_shell = False
                if dist_shifted <= radius and dist_shifted >= (radius - wall_thickness):
                    is_shell = True
                    
                # Add Noise / Missing Voxels (Anisotropic Streaks)
                # Scanlines
                
                if (z_mm % 8.0) < 0.5: # Missing scanline
                    is_shell = False
                    
                grid[x_idx,y_idx,z_idx] = is_shell

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "glitch_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
