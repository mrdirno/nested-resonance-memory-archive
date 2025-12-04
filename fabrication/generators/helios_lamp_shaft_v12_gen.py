import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES V12: THE EVENTUALITY (SHAFT)
# -----------------------------------------------------------------------------
# Concept: Signal Decay (Resolution Loss).
# Math: Voxelization / Quantization of coordinates.
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating V12 SHAFT (Signal Decay): {output_path}")

    base_radius = 22.0
    
    core_radius = 7.5 # 15mm ID
    core_wall_radius = 9.0

    step = height / resolution
    max_r = base_radius + 5.0
    
    res_xy = int(2 * max_r / step) + 2
    res_z = int(height / step) + 1

    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    base_scale = 2.0 * math.pi / 15.0

    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Decay Factor: Increases with Height
        # 0.0 at bottom (High Res), 1.0 at top (Low Res)
        decay = z_norm
        
        # Bit Depth (Quantization Step)
        # Start small (smooth), get large (blocky)
        quant_step = 1.0 + (decay * 8.0) # 1mm to 9mm blocks

        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - max_r
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - max_r
                
                dist = math.sqrt(x_mm**2 + y_mm**2)

                # 1. Core Logic (Protected from Decay)
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # 2. Plug Interface
                plug_check = lamp_lib.apply_shaft_plug_v2(z_mm, dist)
                if plug_check is True:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # 3. Top Cap
                if z_mm > (height - 2.0):
                    if dist <= base_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                if dist <= base_radius:
                    # Quantize Coordinates based on Decay
                    qx = round(x_mm / quant_step) * quant_step
                    qy = round(y_mm / quant_step) * quant_step
                    qz = round(z_mm / quant_step) * quant_step
                    
                    # Gyroid on Quantized Coords
                    val = math.sin(qx * base_scale) * math.cos(qy * base_scale) + \
                          math.sin(qy * base_scale) * math.cos(qz * base_scale) + \
                          math.sin(qz * base_scale) * math.cos(qx * base_scale)
                    
                    if abs(val) < 0.5:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r, 2*max_r)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "shaft_v12.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
