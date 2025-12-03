import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE SWARM (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Nesting Ground (Chaotic Swirl), Library Integration.
# Logic: Nesting Ground (Swirling Fluid).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating SWARM BASE (v2.0): {output_path}")
    
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
    
    # Flow Pattern (v2.0: Stronger Swirl)
    scale = 2.0 * math.pi / 35.0
    
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
                    # Swirl Relief (Chaotic)
                    # Warp domain based on angle
                    angle = math.atan2(y_mm, x_mm)
                    
                    # Swirl: Rotate coordinates proportional to radius
                    twist = dist * 0.1
                    x_rot = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    y_rot = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    val = math.sin(x_rot * scale) + math.sin(y_rot * scale * 1.5)
                    
                    # Height map
                    h_mod = (val + 2.0) / 4.0
                    z_surf = height - 8.0 * (1.0 - h_mod)
                    
                    # Bevel edge
                    if dist > (radius - 5.0): z_surf = height - 2.0
                    
                    if z_mm < 4.0: grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf: grid[x_idx,y_idx,z_idx] = True
                    else: grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "swarm_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
