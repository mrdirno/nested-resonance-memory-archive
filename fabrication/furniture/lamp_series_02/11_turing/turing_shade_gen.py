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
# HELIOS LAMP SERIES 02: THE TURING (SHADE)
# -----------------------------------------------------------------------------
# Logic: Reaction-Diffusion (Turing Pattern)
# Method: Multi-scale noise approximation of Turing Spots/Stripes
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall)
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE TURING SHADE: {output_path}")
    
    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # 40mm Hub
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = (diameter / 2.0) - wall_thickness # Exact 1 inch rim
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Turing Pattern Simulation (Approximation)
    # Using harmonic addition of sine waves to simulate Reaction-Diffusion spots/stripes
    # A mix of frequencies creates the "fingerprint" look.
    
    # Base Scales
    scale_1 = 2.0 * math.pi / 35.0 
    scale_2 = 2.0 * math.pi / 18.0 
    
    print("Calculating Reaction-Diffusion Field...")
    
    radius = diameter / 2.0
    
    # Center offset for Z (Cylinder/Dome hybrid)
    # Let's make it a rounded cylinder
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
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
                         if dist_xy < radius: # Connected to shell
                             grid[x_idx,y_idx,z_idx] = True
                             continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: SHELL BODY (Anisotropic Turing) ---
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Anisotropy: Stretch vertically (Biological Growth)
                sx = scale_1
                sy = scale_1
                sz = scale_1 * 0.5 # Stretched Z
                
                sx2 = scale_2
                sy2 = scale_2
                sz2 = scale_2 * 0.5
                
                v1 = math.sin(x_mm * sx) + math.sin(y_mm * sy) + math.sin(z_mm * sz)
                v2 = math.cos(x_mm * sx2) * math.cos(y_mm * sy2) * math.cos(z_mm * sz2)
                
                val = v1 + 0.5 * v2
                
                if abs(val) < 0.5:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "turing_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
