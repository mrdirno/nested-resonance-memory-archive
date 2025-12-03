import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic: 
# 1. 1-Inch Thick Wall (Robustness).
# 2. 200mm Diameter (Max Print Area).
# 3. Connection Guarantee: Flattened Top Shell to ensure Spokes connect to something.
# 4. Refined Hub: 40mm Diameter (Spider Fitter).
# 5. Refined Bottom Rim: 4mm Thick.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating EVENT HORIZON SHADE (V7 CONNECTION FIX): {output_path}")
    
    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # 40mm Dia
    spoke_width = 8.0 
    top_plate_height = 4.0
    
    # Bottom Rim (Refined)
    bottom_rim_height = 4.0 
    
    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Frequency Setup
    target_period = 48.5
    start_scale = 2.0 * math.pi / 60.0
    end_scale = 2.0 * math.pi / target_period
    
    print("Calculating Field...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Scale
        current_scale = start_scale * (1.0 - z_norm) + end_scale * z_norm
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Calculate Spherical Distance
                # CONNECTION GUARANTEE: Flatten the top of the sphere mathematically
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # --- PRIORITY 1: SPIDER FITTER (Library Call) ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_from_center_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: SHELL & PATTERN ---
                
                is_solid = False
                
                # 1. Shell Definition
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                
                # 2. Hand Access
                in_hand_void = dist_from_center_xy < hand_access_radius
                is_void = in_inner_void or in_hand_void
                
                if in_outer_shell and not is_void:
                    # Pattern
                    lx = x_mm * current_scale
                    ly = y_mm * current_scale
                    lz = z_mm * current_scale
                     
                    sx, sy, sz = math.sin(lx), math.sin(ly), math.sin(lz)
                    cx, cy, cz = math.cos(lx), math.cos(ly), math.cos(lz)
                     
                    val = sx*sy*sz + sx*cy*cz + cx*sy*cz + cx*cy*sz
                    
                    if abs(val) < 0.35: 
                        is_solid = True
                        
                # --- PRIORITY 3: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and not in_hand_void:
                         is_solid = True
                         
                grid[x_idx,y_idx,z_idx] = is_solid

    print("Extracting Mesh...")
    # Manual extraction for now (or use library if compatible)
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_y):
                y_mm = (y * step) - (diameter/2)
                
                if not grid[x,y,z]: continue
                s2 = step/2
                
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/02_event_horizon/event_horizon_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)