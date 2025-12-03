import numpy as np
import math
import sys
import struct
import random
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE DARK MATTER (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Filamentary Web (Dense), Library Integration.
# Logic: Void Anchor (Ring-like structure, negative space).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating DARK MATTER BASE (v2.0): {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 
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
    
    # Voronoi Void Pattern (Denser for v2.0)
    num_points = 80 # Increased density
    points = []
    random.seed(2025)
    for _ in range(num_points):
        px = random.uniform(-diameter/2, diameter/2)
        py = random.uniform(-diameter/2, diameter/2)
        pz = random.uniform(-5, height+5)
        points.append((px, py, pz))

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
                     # Voronoi Logic
                    d1 = 9999.0
                    d2 = 9999.0
                    for p in points:
                        px, py, pz = p
                        d = (x_mm-px)**2 + (y_mm-py)**2 + (z_mm-pz)**2
                        if d < d1:
                            d2 = d1
                            d1 = d
                        elif d < d2:
                            d2 = d
                    d1 = math.sqrt(d1)
                    d2 = math.sqrt(d2)
                    
                    # Web Structure
                    # Solid if near edge (d2-d1 small)
                    
                    # Force Solid Rim at Top and Bottom
                    if z_mm < 4.0 or z_mm > (height - 4.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Force Solid Center for stability
                    if dist < 25.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    if (d2 - d1) < 5.0: # Thinner, denser web
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "dark_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)