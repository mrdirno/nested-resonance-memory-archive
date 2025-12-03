import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE LATTICE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Nanotube (Hexagonal Prism Lattice).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating LATTICE SHAFT: {output_path}")
    
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
    
    # Hexagonal Prism Logic
    sides = 6
    
    # Lattice Params
    l_scale = 15.0
    strut_r = 2.5
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Tapered Hexagon
        # radius varies slightly
        current_radius = base_radius * 0.9
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # Hexagon Boundary
                sector = 2*math.pi / sides
                a_quant = math.floor(angle / sector) * sector + (sector/2)
                d_hex = dist * math.cos(angle - a_quant)
                r_hex = current_radius * math.cos(sector/2)
                
                in_hex = d_hex < r_hex
                
                # V4 QA Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if in_hex:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Lattice Structure (Nanotube - Anisotropic)
                if in_hex:
                    # Anisotropy: Stretch Z (Nanotube elongation)
                    sz = 0.5
                    
                    # Map to Lattice Space
                    lx = x_mm / l_scale
                    ly = y_mm / l_scale
                    lz = (z_mm / l_scale) * sz
                    
                    dx = abs(lx - round(lx))
                    dy = abs(ly - round(ly))
                    dz = abs(lz - round(lz))
                    
                    is_strut = False
                    th = strut_r / l_scale
                    
                    # Vertical struts (XY distance) are standard
                    if math.sqrt(dx*dx + dy*dy) < th: is_strut = True
                    # Horizontal struts (XZ, YZ distance) are stretched in Z
                    # Effective thickness in Z is increased?
                    if math.sqrt(dx*dx + dz*dz) < th: is_strut = True
                    if math.sqrt(dy*dy + dz*dz) < th: is_strut = True
                    
                    if is_strut:
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
    output_file = "lattice_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
