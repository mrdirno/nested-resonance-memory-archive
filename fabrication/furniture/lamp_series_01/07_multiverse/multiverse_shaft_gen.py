import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE MULTIVERSE (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Stacked Spheres (Tight Packing), Library Integration.
# Logic: Stacked Spheres/Bubbles.
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating MULTIVERSE SHAFT (v2.0): {output_path}")
    
    # Dimensions
    max_radius = 25.0
    
    # Core
    core_radius = 7.0 # 14mm ID (V4 Std)
    core_wall_radius = 9.0
    
    step = height / resolution
    
    res_x = int(2 * max_radius / step) + 2
    res_y = int(2 * max_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Bubble Stack Params (v2.0: More bubbles)
    num_bubbles = 8 
    bubble_spacing = height / num_bubbles
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Find nearest bubble center
        # z = i * spacing + offset
        
        # Center of bubbles along Z
        # Use modulo to find distance to nearest center
        
        dist_to_center_z = (z_mm % bubble_spacing) - (bubble_spacing / 2.0)
        
        # Radius profile of a sphere: r = sqrt(R^2 - z^2)
        # Max radius R = max_radius
        
        # Normalized dist from center (-1 to 1)
        norm_dist = dist_to_center_z / (bubble_spacing / 2.0)
        
        # Radius at this Z
        # Ellipsoidal to fit spacing
        # r(z) = R_max * sqrt(1 - norm_dist^2)
        
        # Add overlap?
        # Make spheres slightly larger than spacing to overlap
        
        sphere_r_z = (bubble_spacing / 2.0) * 1.2 # 20% overlap
        
        if abs(dist_to_center_z) < sphere_r_z:
            current_radius = max_radius * math.sqrt(1.0 - (dist_to_center_z/sphere_r_z)**2)
        else:
            current_radius = 0.0
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (max_radius - 5.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Outer Shell
                if dist <= current_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_radius, 2*max_radius)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "multiverse_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)