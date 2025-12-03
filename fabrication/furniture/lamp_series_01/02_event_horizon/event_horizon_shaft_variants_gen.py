import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: EVENT HORIZON SHAFT VARIATIONS
# -----------------------------------------------------------------------------

def write_binary_stl(filename, vertices, faces):
    # ... (Standard STL writer, utilizing lamp_lib in practice, but inlining for brevity if needed)
    # Actually, let's use lamp_lib.write_binary_stl
    pass

def generate_shaft_variant(output_path, 
                           style="medium", 
                           height=180.0, 
                           resolution=120):
    
    print(f"Generating Event Horizon Shaft ({style}): {output_path}")
    
    # Common Params
    core_radius = 7.0
    core_wall_radius = 9.0
    
    # Style Specifics
    if style == "medium":
        base_radius = 15.0
        max_bulge = 12.0
        twist_freq = 2.0 # Standard twist
        taper_mode = "bulge"
    elif style == "large":
        base_radius = 18.0
        max_bulge = 18.0 # Huge waves
        twist_freq = 1.5 # Slower twist
        taper_mode = "bulge"
    elif style == "conic":
        base_radius = 25.0
        top_radius = 15.0
        max_bulge = 5.0 # Subtle ripple
        twist_freq = 3.0 # High twist
        taper_mode = "cone"
        
    # Bounds
    if taper_mode == "bulge":
        max_r_bound = base_radius + max_bulge + 5.0
    else:
        max_r_bound = max(base_radius, top_radius) + max_bulge + 5.0
        
    step = height / resolution
    res_x = int(2 * max_r_bound / step) + 2
    res_y = int(2 * max_r_bound / step) + 2
    res_z = int(height / step) + 1
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # 1. Profile
        if taper_mode == "bulge":
            bulge = max_bulge * math.sin(z_norm * math.pi)
            nominal_radius = base_radius + bulge
        else:
            # Cone
            nominal_radius = base_radius * (1.0 - z_norm) + top_radius * z_norm
            # Add subtle anisotropy to the cone (breathing)
            nominal_radius += max_bulge * math.sin(z_norm * 4.0 * math.pi) * 0.5
            
        # 2. Twist
        theta = z_norm * twist_freq * 2.0 * math.pi
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_r_bound
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_r_bound
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # Core
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if dist < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Caps
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    if dist < (nominal_radius - 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                # 3. Rib Texture (The "Cool" Part)
                # 8 Ribs
                raw_tex = math.cos(8.0 * angle + theta)
                texture = raw_tex * abs(raw_tex) # Sharpen
                
                # Depth varies with Z
                rib_depth = 3.0 + (2.0 * math.sin(z_norm * math.pi))
                
                effective_r = nominal_radius + (texture * rib_depth)
                
                if dist <= effective_r:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Mesh
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, 2*max_r_bound, 2*max_r_bound)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    generate_shaft_variant("event_horizon_shaft_medium.stl", "medium")
    generate_shaft_variant("event_horizon_shaft_large.stl", "large")
    generate_shaft_variant("event_horizon_shaft_conic.stl", "conic")
