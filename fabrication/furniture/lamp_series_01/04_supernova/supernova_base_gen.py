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
# HELIOS LAMP SERIES 01: THE SUPERNOVA (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: High-Res Facets, Library Integration.
# Logic: Neutron Core (Faceted/Low-Poly).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=45.0, resolution=100):
    print(f"Generating SUPERNOVA BASE (v2.0): {output_path}")
    
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
    
    # Generate Planes for Faceting (v2.0: More facets)
    num_planes = 24 # Increased from 12
    planes = []
    random.seed(2025)
    
    for i in range(num_planes):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0.2, 1.5) 
        nx = math.sin(phi) * math.cos(theta)
        ny = math.sin(phi) * math.sin(theta)
        nz = math.cos(phi)
        
        # Distance variance
        d = radius * random.uniform(0.85, 1.05) 
        planes.append((nx, ny, nz, d))
        
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Features
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist_xy,
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
                if z_mm <= height:
                    # Check planes
                    # Center coords for planes
                    px = x_mm
                    py = y_mm
                    pz = z_mm - (height/2.0) 
                    
                    is_inside = True
                    
                    # Global cylinder check first
                    if dist_xy > radius: is_inside = False
                    
                    if is_inside:
                        for p in planes:
                            nx, ny, nz, d = p
                            # Plane equation: ax + by + cz = d
                            # If dot > d, outside
                            if (px*nx + py*ny + pz*nz) > d:
                                is_inside = False
                                break
                                
                    # Flatten Top for Hardware (20mm radius)
                    if z_mm > (height - 5.0) and dist_xy < 20.0:
                        is_inside = True
                        
                    # Solid Core
                    if dist_xy < 20.0: is_inside = True
                    
                    # Bottom Rim
                    if z_mm < 4.0 and dist_xy < radius:
                        is_inside = True
                        
                    grid[x_idx,y_idx,z_idx] = is_inside
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "supernova_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)