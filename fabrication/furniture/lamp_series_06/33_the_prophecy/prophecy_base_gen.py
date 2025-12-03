import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE PROPHECY (BASE)
# -----------------------------------------------------------------------------
# Logic: Seer's Pedestal (Pyramid/Eye).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Triangular/Pyramidal relief.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating PROPHECY BASE: {output_path}")
    
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
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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
                    # Pyramid Relief
                    # 3-sided pyramid (Eye of Providence style)
                    
                    # Distance to triangle boundary?
                    # r * cos(theta - closest_vertex_angle) ?
                    
                    num_sides = 3
                    sector = 2*math.pi/num_sides
                    a_quant = math.floor(angle / sector) * sector + (sector/2)
                    d_tri = dist * math.cos(angle - a_quant)
                    
                    # Height is proportional to d_tri?
                    # Pyramid peak at center
                    
                    # Simple cone: h = H * (1 - r/R)
                    # Pyramid: h = H * (1 - d_tri / R_tri)
                    
                    # Base is circular, but relief is triangular
                    
                    h_mod = 1.0 - (d_tri / (radius*0.8))
                    if h_mod < 0: h_mod = 0
                    
                    z_surf = height * h_mod
                    
                    # Add "Eye" in middle?
                    # Flat top
                    if dist < 20.0: z_surf = height - 5.0
                    
                    # Flatten rim
                    if dist > (radius - 5.0): z_surf = height - 2.0
                    
                    # Minimum thickness
                    z_surf = max(z_surf, 5.0)
                    
                    if z_mm < 4.0: 
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "prophecy_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
