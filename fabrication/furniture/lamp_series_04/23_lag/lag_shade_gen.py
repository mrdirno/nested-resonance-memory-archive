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
# HELIOS LAMP SERIES 04: THE LAG (SHADE)
# -----------------------------------------------------------------------------
# Logic: Latency / Datamosh (Smeared Geometry).
# Method: Sheared coordinates (motion blur effect).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE LAG SHADE (DATAMOSH): {output_path}")
    
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
    
    # Lag Logic
    # Simulate a "drag" effect.
    # x' = x + velocity * time
    # But we want chunks to lag behind.
    
    # Define "Time" as Z axis.
    # Define "Lag Zones" where x/y get shifted significantly.
    
    print("Simulating Latency...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Define Lag Offset
        # Blocky sine wave for shear
        # step function
        
        lag_x = 0.0
        lag_y = 0.0
        
        # 3 Major Lag spikes
        if z_norm > 0.2 and z_norm < 0.3:
            lag_x = 15.0
        if z_norm > 0.5 and z_norm < 0.55:
            lag_y = -20.0
        if z_norm > 0.75 and z_norm < 0.85:
            lag_x = -10.0
            lag_y = 10.0
            
        # Add high frequency jitter (packet loss)
        if (z_idx % 10) < 2:
            lag_x += 5.0
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                # Shifted Coords
                xs = x_mm - lag_x
                ys = y_mm - lag_y
                
                # Distance in shifted space
                dist_s = math.sqrt(xs**2 + ys**2)
                
                # Distance in real space (for mounting)
                dist_real = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_real,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM (REAL SPACE) ---
                if z_mm < bottom_rim_height:
                    if dist_real < radius and dist_real > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: LAG SHELL (SHIFTED SPACE) ---
                
                is_solid = False
                
                # Bounds check in Shifted space
                if dist_s <= radius and dist_s >= (radius - wall_thickness):
                    # Scanlines
                    scanline = math.sin(z_mm * 2.0)
                    if scanline <= 0.9:
                        is_solid = True
                        
                # CONNECTIVITY SPINE (Real Space)
                # A vertical frame that holds the shifted layers together
                # 4 vertical pillars at r=70
                
                angle_real = math.atan2(y_mm, x_mm)
                in_pillar = False
                
                # Pillars at 0, 90, 180, 270
                pillar_angle_width = 0.1
                if abs(math.sin(2*angle_real)) < pillar_angle_width:
                    if dist_real > (radius - wall_thickness - 5.0) and dist_real < (radius + 5.0):
                        in_pillar = True
                        
                if in_pillar: is_solid = True
                
                # Ensure hand access in REAL space
                if dist_real < hand_access_radius:
                    is_solid = False
                    
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lag_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
