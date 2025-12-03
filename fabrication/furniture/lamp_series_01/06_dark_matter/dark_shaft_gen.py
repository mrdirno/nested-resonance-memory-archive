import numpy as np
import math
import sys
import struct
import random
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE DARK MATTER (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Twisted Fiber Bundle, Library Integration.
# Logic: Filamentary Void (Bundle of Twisted Strands).
# Features: V4 QA (Solid Core, End Caps).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating DARK MATTER SHAFT (v2.0): {output_path}")
    
    # Dimensions
    base_radius = 25.0
    
    # Core
    core_radius = 7.0 # 14mm ID
    
    step = height / resolution
    
    res_x = int(2 * base_radius / step) + 2
    res_y = int(2 * base_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Strands Setup (v2.0: More strands, complex twist)
    num_strands = 12
    strand_radius = 4.5
    twist_rate = 3.0 * math.pi 
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Rotation at this height
        angle_offset = z_norm * twist_rate
        
        # Radius of bundle varies (Waist)
        bundle_radius = 15.0 * (0.8 + 0.2 * math.cos(z_norm * math.pi * 2))
        
        strand_centers = []
        for i in range(num_strands):
            theta = (i / num_strands) * 2 * math.pi + angle_offset
            # Add slight jitter/braid effect?
            # Twist within twist
            braid = 2.0 * math.sin(z_norm * 10.0 + i)
            
            sx = (bundle_radius + braid) * math.cos(theta)
            sy = (bundle_radius + braid) * math.sin(theta)
            strand_centers.append((sx, sy))
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - base_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - base_radius
                
                dist_sq = x_mm**2 + y_mm**2
                dist = math.sqrt(dist_sq)
                
                is_solid = False
                
                # Check strands
                for sc in strand_centers:
                    sx, sy = sc
                    d_strand = math.sqrt((x_mm-sx)**2 + (y_mm-sy)**2)
                    if d_strand < strand_radius:
                        is_solid = True
                        break
                
                # Central pillar for core channel stability
                if dist < (core_radius + 3.0):
                    is_solid = True

                # Inner Core (Void)
                if dist < core_radius:
                    is_solid = False
                    
                # V4 END CAPS
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist > core_radius and dist < 18.0:
                        is_solid = True
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*base_radius, 2*base_radius)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "dark_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)