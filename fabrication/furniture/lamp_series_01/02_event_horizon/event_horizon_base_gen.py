import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Spiral Gravity Well Relief, Library Integration.
# Logic: Swirling Vortex Accretion Disk.
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating EVENT HORIZON BASE (v2.0): {output_path}")
    
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
                    # STRICT AGPH (Gravity Well)
                    
                    # a(z) - Vertical compression near singularity
                    az = 1.0 + 2.0 * (1.0 - dist/radius)**2 
                    
                    # R(z) - Event Horizon Spin
                    theta = (1.0 - dist/radius) * 6.0 # High spin at center
                    cos_t = math.cos(theta)
                    sin_t = math.sin(theta)
                    
                    tx = x_mm * cos_t - y_mm * sin_t
                    ty = x_mm * sin_t + y_mm * cos_t
                    
                    # Scale
                    freq = 2.0 * math.pi / 25.0
                    lx = tx * freq
                    ly = ty * freq
                    lz = z_mm * az * freq
                    
                    # Gyroid
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    # Shell Logic
                    if z_mm < 4.0 or z_mm > (height - 4.0):
                         grid[x_idx,y_idx,z_idx] = True
                    elif dist > (radius - 5.0):
                         grid[x_idx,y_idx,z_idx] = True
                    else:
                         if abs(val) < 0.4:
                             grid[x_idx,y_idx,z_idx] = True
                         else:
                             grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "event_horizon_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
