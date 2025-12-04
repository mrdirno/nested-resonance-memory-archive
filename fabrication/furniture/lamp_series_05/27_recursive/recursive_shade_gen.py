import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE RECURSIVE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Droste Effect (Self-Reference).
# Method: Nested Shells / Recursive Subtraction.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE RECURSIVE SHADE: {output_path}")
    
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
    
    # Recursive Logic
    # A sphere inside a sphere inside a sphere.
    # With cutouts to see inside.
    
    # 3 Shells
    radius = diameter / 2.0
    r1 = radius
    r2 = r1 * 0.7
    r3 = r1 * 0.4
    
    # Thickness of each shell layer
    shell_thick = 6.0
    
    print("Recursing...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = r1
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

                # --- PRIORITY 3: RECURSIVE SHELL (Anisotropic) ---
                
                # Layers
                is_solid = False
                
                # Shells logic... simplified for printability
                # Just one thick shell with internal structure
                
                if dist_xy <= r1 and dist_xy >= (r1 - 20.0):
                    # Thick outer shell
                    # Cut windows
                    
                    # Anisotropy: Stretch Z
                    scale = 2.0 * math.pi / 40.0
                    sz = scale * 0.5
                    
                    window_val = math.sin(x_mm * scale) * math.sin(y_mm * scale) * math.sin(z_mm * sz)
                    
                    if window_val > 0.55: # Smaller windows (was 0.6)
                        is_solid = False
                    else:
                        is_solid = True
                        
                # Hand access
                if dist_xy < hand_access_radius: is_solid = False
                
                # Outer bound
                if dist_xy > r1: is_solid = False
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "recursive_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
