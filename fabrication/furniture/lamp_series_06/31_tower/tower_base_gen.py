import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE TOWER (BASE)
# -----------------------------------------------------------------------------
# Logic: City Block (Grid/Plaza).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Grid streets and building footprints.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating TOWER BASE: {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 # 14mm
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
    
    # City Grid
    block_size = 15.0
    street_width = 4.0
    
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
                    # Truss Logic (v2.0 - Anisotropic)
                    # Load Paths
                    
                    # Radial ribs (X/Y Anisotropy)
                    angle = math.atan2(y_mm, x_mm)
                    
                    num_ribs = 8
                    in_rib = abs(math.sin(num_ribs/2.0 * angle)) < 0.15 # Thin ribs
                    
                    # Concentric Rings
                    # Z-Anisotropy: Rings get denser at base?
                    # No, load spreading.
                    
                    in_ring = False
                    ring_spacing = 20.0
                    if (dist % ring_spacing) < 4.0: in_ring = True
                    
                    # Height map
                    z_surf = height
                    if dist > (radius - 5.0): z_surf = height
                    if dist > (radius - 2.0): z_surf = 4.0
                    
                    if z_mm < 4.0:
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
                        if in_rib or in_ring:
                            grid[x_idx,y_idx,z_idx] = True
                        else:
                            # Infill lattice (Anisotropic Z-Stretch)
                            # Stretch Z to support vertical load
                            sz = 0.5
                            val = math.sin(x_mm*0.2)*math.cos(y_mm*0.2) + math.sin(z_mm*0.2*sz)
                            if abs(val) < 0.2:
                                grid[x_idx,y_idx,z_idx] = True
                            else:
                                grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "tower_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
