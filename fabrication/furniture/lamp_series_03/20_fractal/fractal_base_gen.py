import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE FRACTAL (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Sierpinski Step Relief, Library Integration.
# Logic: Recursive Grid (Sierpinski Carpet).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating FRACTAL BASE (v2.0): {output_path}")
    
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
    
    # Fractal Pattern (v2.0: Recursive Step)
    def get_sierpinski_depth(x, y, size):
        depth = 0
        s = size / 3.0
        
        # Check iterations
        # Iter 1
        px, py = abs(x), abs(y)
        c1 = 0
        if (px % size) > s and (px % size) < (s*2): c1 += 1
        if (py % size) > s and (py % size) < (s*2): c1 += 1
        if c1 == 2: return 1 # Depth 1 hole
        
        # Iter 2
        s2 = s / 3.0
        c2 = 0
        if (px % s) > s2 and (px % s) < (s2*2): c2 += 1
        if (py % s) > s2 and (py % s) < (s2*2): c2 += 1
        if c2 == 2: return 2 # Depth 2 hole
        
        return 0 # Solid surface
    
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
                    # Menger Sponge Base (v2.0)
                    # Anisotropy: Scale varies radially
                    
                    r_stretch = 1.0 + 0.5 * (dist/radius)
                    
                    px = abs(x_mm * r_stretch)
                    py = abs(y_mm * r_stretch)
                    pz = z_mm
                    
                    is_cut = False
                    
                    # Iteration 1
                    c1 = 0
                    s1 = 20.0
                    if (px % (s1*3)) > s1 and (px % (s1*3)) < (s1*2): c1 += 1
                    if (py % (s1*3)) > s1 and (py % (s1*3)) < (s1*2): c1 += 1
                    if (pz % (s1*3)) > s1 and (pz % (s1*3)) < (s1*2): c1 += 1
                    if c1 >= 2: is_cut = True
                    
                    # Bevel edge logic (height map)
                    z_surf = height
                    if dist > (radius - 15.0):
                        z_surf = height * ((radius - dist)/15.0)
                    if z_surf < 4.0: z_surf = 4.0
                    
                    # Shell
                    if z_mm < 4.0:
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm > z_surf:
                        grid[x_idx,y_idx,z_idx] = False
                    elif is_cut:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fractal_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
