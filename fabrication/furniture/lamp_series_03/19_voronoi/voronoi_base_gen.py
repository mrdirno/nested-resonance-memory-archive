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
# HELIOS LAMP SERIES 03: THE VORONOI (BASE)
# -----------------------------------------------------------------------------
# Logic: Cellular Pavement (Flat Voronoi).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Voronoi cells.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating VORONOI BASE: {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 # 14mm
    foot_radius = 10.0
    foot_depth = 3.0
    foot_offset = 15.0
    channel_height = 8.0
    channel_width = 8.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Voronoi Cells (2D Extruded)
    num_cells = 30
    cells = []
    random.seed(2020)
    
    for _ in range(num_cells):
        r = random.uniform(0, radius)
        theta = random.uniform(0, 2*math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        cells.append((x,y))
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Features
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist,
                    height=height,
                    hole_radius=rod_radius,
                    channel_height=channel_height,
                    channel_width=channel_width,
                    foot_depth=foot_depth,
                    foot_radius=foot_radius,
                    foot_offset=foot_offset,
                    radius=radius
                )
                
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue
                
                # Base Body
                if dist <= radius:
                    # 2D Voronoi Logic (Anisotropic)
                    d1 = 999.0
                    d2 = 999.0
                    
                    # Anisotropy: Stretch Y (Simulate wood grain or flow)
                    sy = 0.5 
                    
                    for c in cells:
                        cx, cy = c
                        d = (x_mm-cx)**2 + ((y_mm-cy)*sy)**2 
                        if d < d1:
                            d2 = d1
                            d1 = d
                        elif d < d2:
                            d2 = d
                            
                    d1 = math.sqrt(d1)
                    d2 = math.sqrt(d2)
                    
                    # Relief pattern
                    val = (d2 - d1)
                    
                    z_surf = height - 5.0 + val
                    if z_surf > height: z_surf = height
                    
                    # Flatten top rim
                    if dist > (radius - 5.0): z_surf = height - 2.0
                    
                    # Solid
                    if z_mm < 4.0:
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "voronoi_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
