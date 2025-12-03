import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE UNSEEN (SHADE)
# -----------------------------------------------------------------------------
# Logic: Camouflage (Moiré / Interference).
# Method: High-frequency interference patterns (Moiré Grid).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE UNSEEN SHADE: {output_path}")
    
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
    
    # Moiré Logic
    # Overlap two high-frequency grids slightly rotated or scaled
    
    print("Cloaking Device Engaged...")
    
    radius = diameter / 2.0
    
    # Pattern 1: Vertical slats
    freq1 = 2.0 * math.pi / 5.0 # 5mm spacing
    
    # Pattern 2: Angled slats
    freq2 = 2.0 * math.pi / 5.2 # Slightly different pitch
    angle_offset = 0.1 # Rads
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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

                # --- PRIORITY 3: UNSEEN SHELL (Anisotropic Moiré) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Moiré Pattern (Layered Shells)
                
                # Anisotropy: Z-Stretch
                # The interference pattern stretches vertically
                
                # Grid 1: Vertical Ribs (Static)
                num_ribs = 60
                v1 = math.sin(num_ribs * angle)
                
                # Grid 2: Spirals (Z-Stretched)
                # Twist rate depends on Z
                twist = z_mm * 0.1 # Slow twist
                v2 = math.sin(num_ribs * (angle + 0.05) + twist)
                
                # Overlap logic
                
                # Radius 1 (Outer pattern)
                r_outer = radius
                r_mid = radius - (wall_thickness/2)
                r_inner = radius - wall_thickness
                
                is_solid = False
                
                # Outer pattern shell
                if dist_xy > r_mid:
                    if v1 > 0.0: is_solid = True
                    
                # Inner pattern shell
                elif dist_xy > r_inner:
                    if v2 > 0.0: is_solid = True
                    
                # Connector Rings (Z-Stretched Spacing)
                spacing = 20.0 + z_norm * 20.0
                if (z_mm % spacing) < 2.0:
                    is_solid = True
                    
                # Hand access override
                if dist_xy < hand_access_radius: is_solid = False
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "unseen_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
