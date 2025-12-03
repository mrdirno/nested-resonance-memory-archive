import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE PROPHECY (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Optic Nerve (Faceted/Bundled).
# Core: 14mm Central Channel (V4 Std).
# Ends: Solid End Caps (V4 Std).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating PROPHECY SHAFT: {output_path}")
    
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
    
    # Optic Nerve Logic
    # Bundle of fibers or faceted crystal structure?
    # "Vision Ray" -> Focused beam.
    
    # Let's do a triangular prism that twists slowly
    sides = 3
    twist_total = math.pi
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        current_radius = base_radius
        angle_offset = z_norm * twist_total
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # V4 QA Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (current_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Prism Shell
                local_angle = angle + angle_offset
                
                sector = 2*math.pi/sides
                a_quant = math.floor(local_angle / sector) * sector + (sector/2)
                d_poly = dist * math.cos(local_angle - a_quant)
                
                if d_poly < (current_radius * 0.7):
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    # Add ribs at corners?
                    # If angle is near sector boundary
                    dist_to_corner = min(abs(local_angle % sector), abs(sector - (local_angle % sector)))
                    
                    # Not easy to get exact corner distance in angular logic
                    # Just use d_poly
                    
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "prophecy_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
