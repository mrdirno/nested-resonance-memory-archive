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
# HELIOS LAMP SERIES 06: THE END (SHADE)
# -----------------------------------------------------------------------------
# Logic: Entropy Death (Disintegration).
# Method: Gradient Noise Erosion.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE END SHADE: {output_path}")
    
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
    
    # Disintegration Logic
    # Perlin-like noise
    # We can use a simple sum of sines for noise if no noise lib is available
    
    scale = 2.0 * math.pi / 30.0
    
    print("Calculating Entropy...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Erosion threshold
        # 0 at bottom (Solid), 1 at top (Empty)
        # Non-linear: Stays solid for a bit, then crumbles
        erosion_prob = max(0.0, (z_norm - 0.2) * 1.25)
        
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

                # --- PRIORITY 3: DISINTEGRATION SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Noise Generation
                # 3D noise approximation
                n1 = math.sin(x_mm * scale) * math.cos(y_mm * scale) * math.sin(z_mm * scale)
                n2 = math.sin(x_mm * scale * 2.1 + 1.2) * math.cos(y_mm * scale * 2.1 + 2.4) * math.sin(z_mm * scale * 2.1)
                
                noise_val = (n1 + 0.5 * n2) / 1.5
                
                # Normalize noise to 0..1 roughly
                # sin range is -1..1
                noise_norm = (noise_val + 1.0) / 2.0
                
                # If noise < erosion, remove
                # We want "solid" where noise > erosion
                
                # To make it look like crumbling, we need connectivity?
                # Voxel grid ensures some connectivity naturally if resolution is high enough.
                
                # Also hand access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                if noise_norm > erosion_prob:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    # Keep some structural "rebar" or just let it float?
                    # Physics says floating is bad for printing.
                    # We need support.
                    # Add vertical streaks that persist longer?
                    
                    # Structural Ribs
                    angle = math.atan2(y_mm, x_mm)
                    rib = math.cos(8.0 * angle)
                    if rib > 0.8 and z_norm < 0.9: # Ribs fade at very top
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "the_end_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
