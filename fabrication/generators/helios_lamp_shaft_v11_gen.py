import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V11: THE HYPER-DIMENSIONAL (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Hypercube Shadow (Tesseract Projection).
# Math: 4D Lattice Slice.
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V11 SHAFT (Hypercube Shadow): {output_path}")

    base_radius = 22.0
    
    core_radius = 7.0
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 15.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Tesseract Rotation
        # We rotate the 4D hypercube as we move up in Z (Time/Height)
        # w coordinate varies with Z
        w = z_mm * 0.2 

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

                # V2 Interface (Plug)
                plug_check = lamp_lib.apply_shaft_plug_v2(z_mm, dist)
                if plug_check is True:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # Top Cap
                if z_mm > (height - 2.0):
                    if dist <= base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                if dist <= base_radius:
                    # 4D Grid Projection
                    # Simple cubic lattice in 4D: sin(x)sin(y)sin(z)sin(w) = 0
                    # We use a thickness threshold
                    
                    lx = x_mm * base_scale
                    ly = y_mm * base_scale
                    lz = z_mm * base_scale
                    lw = w * base_scale
                    
                    # 4D Lattice Equation
                    val = math.cos(lx) + math.cos(ly) + math.cos(lz) + math.cos(lw)
                    
                    # Threshold for 4D is tricky. Range is [-4, 4].
                    # We want an open lattice.
                    is_solid = abs(val) < 0.8
                    
                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v11.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
