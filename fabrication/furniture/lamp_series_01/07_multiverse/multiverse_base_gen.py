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
# HELIOS LAMP SERIES 01: THE MULTIVERSE (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Dense Bubble Aggregate, Library Integration.
# Logic: Bubble Aggregate (Many small universes).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating MULTIVERSE BASE (v2.0): {output_path}")
    
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
    
    # Bubble Aggregate (Denser for v2.0)
    bubbles = []
    random.seed(2025)
    
    # Main central mass
    bubbles.append((0,0,0, radius*0.8))
    
    # Scattered smaller bubbles
    for _ in range(60): # Increased from 20
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(15, radius-10)
        z = random.uniform(0, height)
        rad = random.uniform(8, 20)
        bubbles.append((r*math.cos(theta), r*math.sin(theta), z, rad))
        
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
                if dist <= radius and z_mm <= height:
                     # Bubble Logic
                    is_solid = False
                    
                    # Optimization: Check bounding box of bubble?
                    # Simple loop
                    for b in bubbles:
                        bx, by, bz, br = b
                        d_sq = (x_mm-bx)**2 + (y_mm-by)**2 + (z_mm-bz)**2
                        if d_sq < br**2:
                            is_solid = True
                            break
                    
                    # Force Solid Rim/Center for structure
                    if z_mm < 4.0: is_solid = True
                    if dist < 25.0: is_solid = True # Solid core for stability
                    
                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "multiverse_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)