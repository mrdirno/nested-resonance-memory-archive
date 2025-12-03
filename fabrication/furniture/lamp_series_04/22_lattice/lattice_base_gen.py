import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE LATTICE (BASE)
# -----------------------------------------------------------------------------
# Logic: Crystal Base (Geometric Steps).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Hexagonal close-packing relief.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating LATTICE BASE: {output_path}")
    
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
    
    # Hex Logic
    hex_size = 15.0
    
    def hex_dist(p):
        # Distance to center of hexagon in a grid
        # q, r coordinates
        q = (math.sqrt(3)/3 * p[0] - 1.0/3 * p[1]) / hex_size
        r = (2.0/3 * p[1]) / hex_size
        
        # Axial round
        rx = round(q)
        ry = round(r)
        rz = round(-q-r)
        
        x_diff = abs(rx - q)
        y_diff = abs(ry - r)
        z_diff = abs(rz - (-q-r))
        
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry-rz
        elif y_diff > z_diff:
            ry = -rx-rz
        else:
            rz = -rx-ry
            
        # Center of hex
        center_x = hex_size * (math.sqrt(3) * (rx + rz/2.0)) # wait, axial to cartesian
        # x = size * sqrt(3) * (q + r/2)
        # y = size * 3/2 * r
        
        cx = hex_size * math.sqrt(3) * (rx + ry/2.0)
        cy = hex_size * 1.5 * ry
        
        return math.sqrt((p[0]-cx)**2 + (p[1]-cy)**2)
    
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
                    # Lattice Logic (v2.0 - Anisotropic)
                    # Stretch radially
                    
                    # Map to Polar Lattice? Or warped Cartesian?
                    # Let's warp Cartesian.
                    l_scale = 15.0 # Defined
                    strut_r = 2.5 # Defined
                    
                    r_stretch = 1.0 + 0.5 * (dist/radius)
                    
                    px = x_mm * r_stretch
                    py = y_mm * r_stretch
                    pz = z_mm
                    
                    gx = px / l_scale
                    gy = py / l_scale
                    gz = pz / l_scale
                    
                    dx = abs(gx - round(gx)) * l_scale
                    dy = abs(gy - round(gy)) * l_scale
                    dz = abs(gz - round(gz)) * l_scale
                    
                    # Struts
                    is_strut = False
                    th = strut_r 
                    
                    if math.sqrt(dx*dx + dy*dy) < th: is_strut = True
                    if math.sqrt(dx*dx + dz*dz) < th: is_strut = True
                    if math.sqrt(dy*dy + dz*dz) < th: is_strut = True
                    
                    # Height map (Bevel)
                    z_surf = height - 5.0
                    if dist > (radius - 5.0): z_surf = height
                    if dist > (radius - 2.0): z_surf = 4.0
                    
                    if z_mm < 4.0:
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
                        if is_strut:
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
    output_file = "lattice_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
