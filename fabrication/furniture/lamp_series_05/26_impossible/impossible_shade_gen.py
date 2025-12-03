import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE IMPOSSIBLE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Optical Illusion (Penrose Triangle / Necker Cube).
# Method: Forced Perspective (Distorted geometry that aligns from one angle).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE IMPOSSIBLE SHADE: {output_path}")
    
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
    
    # Impossible Logic
    # Forced Perspective Twist
    # A shape that looks square from bottom but circular from top?
    # Or a Penrose Triangle loop.
    
    # Let's do a "Squircle Twist" where the corners rotate 90 degrees
    # but the edges seem straight?
    
    # Better: "Impossible" Lattice
    # A grid that twists non-uniformly.
    
    print("Bending Reality...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Perspective Distortion
        # Twist rate accelerates
        twist = (z_norm ** 2.0) * (math.pi / 2.0)
        
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

                # --- PRIORITY 3: SHELL BODY (Anisotropic) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Impossible Geometry (Anisotropic Twist)
                
                # Rotated Coordinate Frame
                rx = x_mm * math.cos(-twist) - y_mm * math.sin(-twist)
                ry = x_mm * math.sin(-twist) + y_mm * math.cos(-twist)
                
                scale = 2.0 * math.pi / 40.0
                
                # Warped scale (Z-Anisotropy)
                warp_scale = scale * (1.0 + 0.5 * math.sin(z_norm * math.pi * 4))
                
                v1 = abs(math.cos(rx * warp_scale))
                v2 = abs(math.cos(ry * warp_scale))
                v3 = abs(math.cos(z_mm * scale))
                
                val = v1 + v2 + v3
                
                # Hollow out center of cubes
                if val > 2.2: # Corners
                    grid[x_idx,y_idx,z_idx] = True
                elif val < 1.2: # Centers
                    grid[x_idx,y_idx,z_idx] = False
                else:
                    # Edges
                    if (v1 > 0.8 and v2 > 0.8) or (v1 > 0.8 and v3 > 0.8) or (v2 > 0.8 and v3 > 0.8):
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "impossible_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
