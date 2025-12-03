import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE TESSERACT (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: 4D Axis (Impossible Geometry), Library Integration.
# Logic: 4th Dimension Axis (Twisted Grid with cuts).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating TESSERACT SHAFT (v2.0): {output_path}")
    
    base_radius = 25.0
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Twisted Cuboid
    twist_total = math.pi / 2.0 # 90 deg
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        angle = z_norm * twist_total
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 QA Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (base_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Rotated Square
                rx = x_mm * math.cos(-angle) - y_mm * math.sin(-angle)
                ry = x_mm * math.sin(-angle) + y_mm * math.cos(-angle)
                
                # "Impossible" Geometry Logic
                # Square profile with periodic notches
                
                if max(abs(rx), abs(ry)) < 20.0:
                    is_solid = True
                    
                    # Grid texture (Anisotropic)
                    # Stretch Z
                    
                    tex_x = math.sin(rx * 0.4)
                    tex_y = math.sin(ry * 0.4)
                    tex_z = math.sin(z_mm * 0.2) # Stretched Z (lower freq)
                    
                    # Create void cubes inside the volume
                    if tex_x > 0.5 and tex_y > 0.5 and tex_z > 0.5:
                        is_solid = False
                        
                    if is_solid:
                        grid[x_idx,y_idx,z_idx] = True

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "tesseract_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
