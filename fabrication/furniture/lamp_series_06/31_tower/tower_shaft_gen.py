import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE TOWER (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Elevator Core / Structural Truss.
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating TOWER SHAFT: {output_path}")
    
    base_width = 40.0 # Square profile
    core_radius = 7.0 
    core_wall_radius = 9.0 
    
    max_r_bound = base_width + 10.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Truss Params
    bay_height = 20.0
    strut_width = 4.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
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
                    if max(abs(x_mm), abs(y_mm)) < (base_width/2.0):
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Square Truss Structure (Anisotropic)
                if max(abs(x_mm), abs(y_mm)) <= (base_width/2.0):
                    # Corner columns
                    is_column = False
                    if abs(x_mm) > (base_width/2.0 - strut_width) and abs(y_mm) > (base_width/2.0 - strut_width):
                        is_column = True
                        
                    # X-Bracing (Anisotropic - Stretched Z)
                    # z % bay_height
                    
                    # Increase bay height for Z-stretch effect
                    # Stretch factor
                    z_stretch = 1.5
                    bh = bay_height * z_stretch
                    
                    z_local = z_mm % bh
                    zn = z_local / bh
                    
                    # X-brace on faces
                    is_brace = False
                    
                    on_face_x = abs(x_mm) > (base_width/2.0 - strut_width)
                    on_face_y = abs(y_mm) > (base_width/2.0 - strut_width)
                    
                    if on_face_x or on_face_y:
                        u = 0.0
                        if on_face_x: u = y_mm + (base_width/2.0)
                        else: u = x_mm + (base_width/2.0)
                        
                        un = u / base_width 
                        
                        if abs(un - zn) < 0.1 or abs(un - (1.0-zn)) < 0.1: # Thinner braces
                            is_brace = True
                            
                        if z_local < strut_width:
                            is_brace = True
                            
                    if is_column or is_brace:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "tower_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
