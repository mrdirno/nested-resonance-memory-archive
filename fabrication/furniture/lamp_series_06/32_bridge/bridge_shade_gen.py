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
# HELIOS LAMP SERIES 06: THE BRIDGE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Suspension / Tension (Catenary Cables).
# Method: Catenary curve generation between structural ribs.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE BRIDGE SHADE: {output_path}")
    
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
    
    # Bridge Logic
    # Main Pylons: Vertical structural ribs
    # Cables: Catenary curves hanging between pylons
    
    num_pylons = 4
    
    print("Calculating Tension...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
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

                # --- PRIORITY 3: BRIDGE SHELL (Anisotropic Tension) ---
                
                if dist_xy > (radius + 5.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Pylons (Vertical Structure)
                angle = math.atan2(y_mm, x_mm)
                if angle < 0: angle += 2*math.pi
                
                sector_angle = (2*math.pi) / num_pylons
                angle_in_sector = angle % sector_angle
                
                in_pylon = False
                pylon_width_rad = 0.2
                
                dist_to_pylon = min(angle_in_sector, sector_angle - angle_in_sector)
                
                if dist_to_pylon < (pylon_width_rad / 2.0):
                    if dist_xy > (radius - 15.0) and dist_xy < radius:
                        in_pylon = True
                        
                if in_pylon:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # Cables (Catenary - Anisotropic Sag)
                
                t = (angle_in_sector / sector_angle) * 2.0 - 1.0
                
                num_cables = 12
                # Anisotropy: Cable spacing stretches with Z
                cable_base_spacing = height / num_cables
                
                sag_amount = 15.0
                
                in_cable = False
                
                for i in range(num_cables):
                    # Non-linear spacing (Closer at top)
                    z_norm_cable = i / num_cables
                    z_anchor = height * (z_norm_cable**0.8)
                    
                    z_curve = z_anchor + sag_amount * (t**2 - 1.0)
                    
                    if abs(z_mm - z_curve) < 2.0: 
                        if dist_xy > (radius - 5.0) and dist_xy < radius:
                            in_cable = True
                            
                if in_cable:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False
                    
                # Ensure Hand Access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "bridge_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
