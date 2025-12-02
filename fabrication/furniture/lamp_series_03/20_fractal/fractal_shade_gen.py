import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE FRACTAL (SHADE)
# -----------------------------------------------------------------------------
# Logic: Menger Sponge / Sierpinski Tetrahedron.
# Method: Recursive Subtraction (SDF).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE FRACTAL SHADE: {output_path}")
    
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
    
    # Fractal Logic (Menger Sponge Approximation)
    # We use modulo arithmetic to cut holes at different scales.
    # 3 Iterations.
    
    # Iteration 1 size: 60mm
    s1 = 60.0
    # Iteration 2 size: 20mm
    s2 = 20.0
    # Iteration 3 size: 6.6mm
    s3 = 6.66
    
    print("Iterating Recursion...")
    
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

                # --- PRIORITY 3: FRACTAL SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Menger Sponge Logic
                # If coords are in the middle 1/3 of the block, it's empty.
                # For sponge, we check X, Y, Z. If 2 or more indices are "middle", cut.
                
                # Shift coords to positive for modulo
                px = abs(x_mm)
                py = abs(y_mm)
                pz = z_mm
                
                is_cut = False
                
                # Iteration 1
                c1 = 0
                if (px % (s1*3)) > s1 and (px % (s1*3)) < (s1*2): c1 += 1
                if (py % (s1*3)) > s1 and (py % (s1*3)) < (s1*2): c1 += 1
                if (pz % (s1*3)) > s1 and (pz % (s1*3)) < (s1*2): c1 += 1
                if c1 >= 2: is_cut = True
                
                # Iteration 2
                if not is_cut:
                    c2 = 0
                    if (px % (s2*3)) > s2 and (px % (s2*3)) < (s2*2): c2 += 1
                    if (py % (s2*3)) > s2 and (py % (s2*3)) < (s2*2): c2 += 1
                    if (pz % (s2*3)) > s2 and (pz % (s2*3)) < (s2*2): c2 += 1
                    if c2 >= 2: is_cut = True
                    
                # Iteration 3
                if not is_cut:
                    c3 = 0
                    if (px % (s3*3)) > s3 and (px % (s3*3)) < (s3*2): c3 += 1
                    if (py % (s3*3)) > s3 and (py % (s3*3)) < (s3*2): c3 += 1
                    if (pz % (s3*3)) > s3 and (pz % (s3*3)) < (s3*2): c3 += 1
                    if c3 >= 2: is_cut = True
                
                if is_cut:
                    grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = True

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fractal_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
