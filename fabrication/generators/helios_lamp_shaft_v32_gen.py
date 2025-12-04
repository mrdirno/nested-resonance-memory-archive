import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V32: THE BRIDGE (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Suspension Cable (Tensile Strength).
# Math: Twisted multi-strand cable.
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V32 SHAFT (Suspension Cable): {output_path}")

    base_radius = 22.0
    core_radius = 7.5
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 10.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Cable Twist
        twist = z_mm * 0.15

        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - max_r
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - max_r
                
                dist = math.sqrt(x_mm**2 + y_mm**2)

                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                plug_check = lamp_lib.apply_shaft_plug_v2(z_mm, dist)
                if plug_check is True:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                if z_mm > (height - 2.0):
                    if dist <= base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                if dist <= base_radius:
                    # Cable Logic
                    # Rotate X/Y
                    rx = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                    ry = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                    
                    # Strands are localized high-density regions in the XY plane
                    # sin(rx) + sin(ry) creates grid of columns
                    
                    val = math.sin(rx * base_scale) + math.sin(ry * base_scale)
                    
                    if abs(val) > 1.0: # Strands
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v32.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
