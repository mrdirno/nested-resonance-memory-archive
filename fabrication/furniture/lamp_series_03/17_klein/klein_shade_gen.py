import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE KLEIN (SHADE)
# -----------------------------------------------------------------------------
# Logic: Klein Bottle Loop (Non-Orientable Surface).
# Method: Parametric Klein Bottle Equation mapped to 3D grid.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE KLEIN SHADE: {output_path}")
    
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
    
    # Klein Bottle SDF Approximation
    # Since explicit parametric surfaces are hard to rasterize without sampling,
    # we will use a "Figure 8" torus approximation that self-intersects.
    # Or better: A twisted torus.
    
    print("Folding Space-Time...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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

                # --- PRIORITY 3: KLEIN SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Surface logic
                # We want a surface that twists.
                # Mobius Strip cross section rotated?
                # 1. Define a major radius R
                # 2. At angle theta, the cross section is rotated by theta/2
                
                # R_major = radius - (wall_thickness/2)
                # Cross section shape: Ellipse
                
                # Let's do a "Figure 8" Twist
                # r(theta, z) = R_avg + A * sin(N*theta + z_factor)
                
                twist_z = z_norm * math.pi # 180 deg twist top to bottom
                
                # Klein-ish Surface
                # r_surface = R_avg + 10 * sin(3*angle + twist_z)
                
                r_surface = (radius - wall_thickness/2.0) + 10.0 * math.sin(2.0 * angle + twist_z)
                
                # Is voxel near this surface?
                thickness = 4.0
                if abs(dist_xy - r_surface) < thickness:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    # Add secondary loop?
                    # Inner loop for self-intersection illusion
                    r_surface_2 = (radius - wall_thickness/2.0) - 15.0 * math.sin(2.0 * angle + twist_z + math.pi)
                    if abs(dist_xy - r_surface_2) < thickness:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "klein_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
