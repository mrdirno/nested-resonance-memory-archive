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
# HELIOS LAMP SERIES 02: THE COLONY (SHADE)
# -----------------------------------------------------------------------------
# Logic: DLA (Diffusion-Limited Aggregation) / Lightning Branching.
# Method: Noise-based Domain Warping to simulate branching structures.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE COLONY SHADE (DLA BRANCHING): {output_path}")
    
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
    
    # DLA Approximation via Domain Warping
    # Start with vertical lines (sine waves)
    # Warp them heavily with noise to create "lightning" paths
    
    # 1. Base Field: Radial Sine (Rings) + Vertical Sine (Columns)?
    # We want branching from bottom up.
    
    # Let's use a "Vein" noise function.
    # 1 - abs(sin(x)) creates lines.
    
    scale_vein = 2.0 * math.pi / 40.0
    
    print("Simulating Aggregation...")
    
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

                # --- PRIORITY 3: SHELL BODY ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Branching Pattern
                # f(p) = 1 / (dist to nearest branch)
                # Approximation: Sum of Abs Sines
                
                # 3 Layers of noise rotated
                # v1 = 1 - abs(sin(x*s))
                # v2 = 1 - abs(sin(rot(x,y)*s*2))
                
                # Rotate coords
                ang1 = 0.5
                x1 = x_mm * math.cos(ang1) - y_mm * math.sin(ang1)
                y1 = x_mm * math.sin(ang1) + y_mm * math.cos(ang1)
                
                ang2 = 1.0
                x2 = x_mm * math.cos(ang2) - y_mm * math.sin(ang2)
                y2 = x_mm * math.sin(ang2) + y_mm * math.cos(ang2)
                
                v1 = abs(math.sin(x_mm * scale_vein) * math.sin(y_mm * scale_vein) * math.sin(z_mm * scale_vein))
                v2 = abs(math.sin(x1 * scale_vein * 1.5) * math.sin(y1 * scale_vein * 1.5) * math.sin(z_mm * scale_vein * 1.5))
                v3 = abs(math.sin(x2 * scale_vein * 2.5) * math.sin(y2 * scale_vein * 2.5))
                
                # Intersection of veins
                # High value where all are low? No.
                # We want thin structures.
                # Let's try: 1.0 - max(v1, v2)
                
                val = (v1 + v2 + v3) / 3.0
                
                # If val is low, we are near zero-crossing (vein center)
                if val < 0.15:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "colony_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
