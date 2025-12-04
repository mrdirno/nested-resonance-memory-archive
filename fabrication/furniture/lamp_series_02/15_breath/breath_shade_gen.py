import numpy as np
import math
import sys
import struct
import os
import random

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE BREATH (SHADE)
# -----------------------------------------------------------------------------
# Logic: Peristalsis (Dynamic Pulse).
# Method: Sine-modulated radius with soft, organic smoothing.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE BREATH SHADE (PERISTALSIS): {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = (diameter / 2.0) - wall_thickness # Exact 1 inch rim
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Peristalsis Logic
    # R(z) = R_base + A * sin(k*z)
    # Soft organic feel -> Low frequency
    
    freq = 2.0 * math.pi / 60.0 # 60mm wave
    amplitude = 15.0
    
    print("Simulating Respiration...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Pulse function
        pulse = math.sin(z_mm * freq)
        
        # Radius modulation
        # Base radius shrinks slightly at top
        current_base_r = radius * (1.0 - 0.2 * (z_mm/height))
        
        current_r = current_base_r + (pulse * amplitude)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: MOUNT (Cantilever Bar/Ring) ---
                if z_mm > (height - 6.0): # Top 6mm
                    # Central Hub (Solid)
                    if dist_xy < 22.0 and dist_xy > 7.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    # Hole
                    if dist_xy <= 7.0:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # Cantilever Bars (Spokes)
                    spoke_angle = math.atan2(y_mm, x_mm)
                    if math.cos(3.0 * spoke_angle) > 0.9: 
                         if dist_xy < current_r: # Connected to shell
                             grid[x_idx,y_idx,z_idx] = True
                             continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: SHELL BODY ---
                
                # Inner Hand Access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Pulse Shell
                r_outer = current_r
                r_inner = current_r - wall_thickness
                
                if r_inner < hand_access_radius: r_inner = hand_access_radius
                
                # WIREFRAME SKIN (Independent)
                if abs(dist_xy - r_outer) < 2.0: 
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                if abs(dist_xy - r_inner) < 2.0: 
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                if dist_xy <= r_outer and dist_xy >= r_inner:
                    # Add Gyroid texture (Anisotropic)
                    # Stretch Z to match the pulse direction
                    
                    sz = 2.0 * math.pi / 20.0 * 0.5 # Stretched Z
                    sxy = 2.0 * math.pi / 20.0
                    
                    val = math.sin(x_mm*sxy)*math.cos(y_mm*sxy) + \
                          math.sin(y_mm*sxy)*math.cos(z_mm*sz) + \
                          math.sin(z_mm*sz)*math.cos(x_mm*sxy)
                          
                    if abs(val) < 0.6: # Thickened (was 0.4)
                        grid[x_idx,y_idx,z_idx] = True
                    
                    # CONNECTIVITY SKELETON
                    # Vertical Ribs to bind the pulses
                    angle = math.atan2(y_mm, x_mm)
                    rib_val = math.cos(8.0 * angle)
                    if rib_val > 0.8:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "breath_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
