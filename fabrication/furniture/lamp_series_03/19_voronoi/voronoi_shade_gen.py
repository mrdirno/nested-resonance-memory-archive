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
# HELIOS LAMP SERIES 03: THE VORONOI (SHADE)
# -----------------------------------------------------------------------------
# Logic: 3D Voronoi Foam (Cellular Partition).
# Method: Scatter points, calculate distance to nearest 2 points (F2-F1 edge).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=100, hole_diameter=14.0):
    print(f"Generating THE VORONOI SHADE: {output_path}")
    
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
    
    # Voronoi Setup
    # We want "Foam" -> Edges are solid.
    # Metric: d2 - d1 < thickness
    
    num_cells = 60
    cells = []
    random.seed(1999)
    
    # Distribute cells in cylinder volume
    for _ in range(num_cells):
        r = random.uniform(0, diameter/2 + 20)
        theta = random.uniform(0, 2*math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = random.uniform(-20, height+20)
        cells.append((x,y,z))
        
    print("Partitioning Space...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
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

                # --- PRIORITY 3: VORONOI SHELL (Anisotropic) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Find 2 closest points
                d1 = 99999.0
                d2 = 99999.0
                
                # Anisotropy: Radial Stretch
                # Cells are longer radially
                # Or Z stretch?
                # Let's do Z stretch for "Stacked Foam"
                sz = 0.5
                
                for c in cells:
                    cx, cy, cz = c
                    # Optimize
                    if abs(z_mm - cz) > 50.0: continue
                    
                    d_sq = (x_mm-cx)**2 + (y_mm-cy)**2 + ((z_mm-cz)*sz)**2
                    if d_sq < d1:
                        d2 = d1
                        d1 = d_sq
                    elif d_sq < d2:
                        d2 = d_sq
                        
                d1 = math.sqrt(d1)
                d2 = math.sqrt(d2)
                
                # Edge thickness
                if (d2 - d1) < 3.0: # 3mm strands
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "voronoi_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
