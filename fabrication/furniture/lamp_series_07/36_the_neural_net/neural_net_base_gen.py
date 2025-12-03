import numpy as np
import math
import sys
import struct
import os
import random # Imported

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 07: THE NEURAL NET (BASE)
# -----------------------------------------------------------------------------
# Logic: Circuit Substrate (PCB Traces).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Geometric trace relief.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating NEURAL NET BASE: {output_path}")
    
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
    
    # Generate Surface Nodes
    random.seed(101)
    surface_nodes = []
    num_nodes = 20
    node_r = 5.0
    
    for _ in range(num_nodes):
        r = random.uniform(10, radius-5)
        theta = random.uniform(0, 2*math.pi)
        surface_nodes.append((r*math.cos(theta), r*math.sin(theta)))
    
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
                    # Neural Logic (v2.0)
                    # Network nodes on surface
                    
                    # Anisotropy: Radial Nodes stretch
                    
                    is_solid = False
                    
                    # Nodes
                    for n in surface_nodes:
                        nx, ny = n
                        # Stretch distance
                        dx = x_mm - nx
                        dy = y_mm - ny
                        
                        # Radial vector
                        angle = math.atan2(ny, nx)
                        
                        # Project d onto radial and tangential
                        dr = dx*math.cos(angle) + dy*math.sin(angle)
                        dt = -dx*math.sin(angle) + dy*math.cos(angle)
                        
                        # Stretch radial
                        if math.sqrt((dr/2.0)**2 + dt**2) < node_r:
                            is_solid = True
                            break
                    
                    if is_solid:
                        z_surf = height
                    else:
                        # Edges?
                        # Voronoi height map
                        d1 = 999.0
                        for n in surface_nodes:
                            d = math.sqrt((x_mm-n[0])**2 + (y_mm-n[1])**2)
                            if d < d1: d1 = d
                        
                        z_surf = height - 5.0 - (d1 * 0.2)
                        if z_surf < 4.0: z_surf = 4.0
                    
                    if z_mm <= z_surf:
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
    output_file = "neural_net_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
