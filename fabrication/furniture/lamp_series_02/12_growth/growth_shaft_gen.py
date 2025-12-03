import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE GROWTH (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Strangler Fig (Dense Wrapping), Library Integration.
# Logic: Vine Twisted (Organic Growth).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating GROWTH SHAFT (v2.0): {output_path}")
    
    base_radius = 25.0
    core_radius = 7.0 # 14mm ID
    core_wall_radius = 9.0 
    
    max_r_bound = base_radius + 5.0
    step = height / resolution
    
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Vines (v2.0: Strangler Fig)
    # Many random vines wrapping around
    num_vines = 6 # Increased
    
    # Seed random phase offsets
    import random
    random.seed(2025)
    vine_phases = [random.uniform(0, 2*math.pi) for _ in range(num_vines)]
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height 
        
        # Organic core shape
        pillar_r = 10.0 + 2.0 * math.sin(z_norm * math.pi * 6)
        
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
                
                # Strangler Vines (Anisotropic - Vertical Stretch)
                is_vine = False
                
                # Anisotropy: Stretch vine logic vertically (less twisting per mm Z)
                # Twist rate is already 3.0 per height... reduce?
                # No, make thickness vary slower in Z
                
                for i in range(num_vines):
                    # Twist rate varies per vine
                    rate = 3.0 + (i % 3)
                    angle_base = vine_phases[i] + z_norm * rate * math.pi
                    
                    # Radial wobble
                    r_vine_center = 18.0 + 3.0 * math.sin(z_mm * 0.05 + i)
                    
                    vx = r_vine_center * math.cos(angle_base)
                    vy = r_vine_center * math.sin(angle_base)
                    
                    d_vine = math.sqrt((x_mm-vx)**2 + (y_mm-vy)**2)
                    
                    # Vine thickness varies slowly (Vertical bias)
                    thickness = 5.0 + 1.5 * math.sin(z_norm * 10.0 + i)
                    
                    if d_vine < thickness:
                        is_vine = True
                        break
                
                if is_vine:
                    grid[x_idx,y_idx,z_idx] = True

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "growth_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
