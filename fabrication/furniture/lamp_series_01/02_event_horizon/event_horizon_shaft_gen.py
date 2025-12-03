import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Accretion Helix (Deeper, Tighter Twist).
# Logic: Gravitational Lensing + Twisted Ribs.
# Features: V4 QA (Solid Core, End Caps, 14mm Clearance).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating EVENT HORIZON SHAFT (v2.0): {output_path}")
    
    base_radius = 15.0 
    max_bulge = 12.0 
    core_radius = 7.0 
    core_wall_radius = 9.0 # Solid core
    
    width = (base_radius + max_bulge + 5.0) * 2.0 
    
    step = width / resolution
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Texture Frequencies (v2.0: Faster twist)
    twist_freq = 4.0 * math.pi / height # 2 full turns
    rib_freq = 8.0 # 8 prominent ribs
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # 1. Gravitational Lensing (Profile Radius)
        bulge = max_bulge * math.sin(z_norm * math.pi)
        nominal_radius = base_radius + bulge
        
        # Twist Angle
        angle_offset = z_mm * twist_freq
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (width/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (width/2)
                
                dist_center = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # V4 Core
                if dist_center < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist_center < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # End Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist_center < (base_radius - 1.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Complex Surface
                # Sharper ribs: cos^3?
                raw_tex = math.cos((angle + angle_offset) * rib_freq)
                # Sharpen
                texture = raw_tex * abs(raw_tex) 
                
                rib_depth = 3.0 + (3.0 * math.sin(z_norm * math.pi))
                effective_radius = nominal_radius + (texture * rib_depth)
                
                if dist_center <= effective_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, width, width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "event_horizon_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
