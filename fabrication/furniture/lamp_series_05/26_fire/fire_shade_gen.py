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
# HELIOS LAMP SERIES 05: THE FIRE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Plasma / Combustion.
# Method: Vertical Perlin Noise (Flame tongues).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE FIRE SHADE: {output_path}")
    
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
    
    # Flame Logic
    # Noise stretched on Z axis
    # Tapering at top like a flame
    
    scale_x = 2.0 * math.pi / 40.0
    scale_z = 2.0 * math.pi / 120.0 # Stretched
    
    print("Igniting Plasma...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Base radius tapers like a flame
        # Wide bottom, pointy top
        # Curve: 1 - z^2 ?
        current_radius = radius * (1.0 - 0.6 * z_norm**1.5)
        
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

                # --- PRIORITY 3: FIRE SHELL ---
                
                if dist_xy > (radius + 10.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Flame Noise
                # Warp X/Y with Z
                
                # Add twist?
                angle = math.atan2(y_mm, x_mm)
                twist = z_mm * 0.02
                
                nx = dist_xy * math.cos(angle + twist)
                ny = dist_xy * math.sin(angle + twist)
                
                # Noise function
                # 3 layers
                v1 = math.sin(nx * scale_x) * math.sin(ny * scale_x) * math.sin(z_mm * scale_z)
                v2 = math.sin(nx * scale_x * 2.0) * math.sin(ny * scale_x * 2.0 + z_mm*0.1)
                
                val = v1 + 0.5 * v2
                
                # Flame structure
                # Shell at current_radius
                # Displace radius by noise
                
                r_disp = current_radius + val * 15.0
                
                # Thickness
                if abs(dist_xy - r_disp) < (wall_thickness / 2.0):
                    # Eroded holes near top?
                    if z_norm > 0.6 and val > 0.8:
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
    output_file = "fire_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
