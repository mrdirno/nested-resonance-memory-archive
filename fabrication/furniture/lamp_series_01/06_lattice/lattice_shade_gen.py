import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE LATTICE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Schwarz P Surface (Primitive) - Cubic Cell Lattice
# Shape: Cylinder (Diameter 180mm, Height 200mm)
# Mount: Spider Fitter V7 (Connected to Shell)
# Wall: 1 Inch Thick (Robust)
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=180.0, height=200.0, resolution=100, hole_diameter=14.0):
    print(f"Generating THE LATTICE SHADE: {output_path}")
    print(f"Dims: {diameter}mm Dia x {height}mm H")
    
    # Mount Parameters (Standard V7)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # Solid central disk
    spoke_width = 8.0 
    top_plate_height = 4.0 
    bottom_rim_height = 4.0 
    
    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = 42.0 # 84mm Diameter hand access
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_xy = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Lattice Parameters (Schwarz P)
    # Periodicity: 30mm
    period = 30.0
    freq = 2.0 * math.pi / period
    
    print("Calculating Field...")
    
    radius = diameter / 2.0
    inner_radius_shell = radius - wall_thickness
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Global Cylinder Limit
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- PRIORITY 1: SPIDER FITTER (Library Call) ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=inner_radius_shell 
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM (Solid Ring) ---
                if z_mm < bottom_rim_height:
                    if dist_xy > inner_radius_shell:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                        continue

                # --- PRIORITY 3: HAND ACCESS (Keep Out Zone) ---
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # --- PRIORITY 4: LATTICE SHELL ---
                # Only exist within the Wall Thickness
                if dist_xy < inner_radius_shell:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Schwarz P Equation: cos(x) + cos(y) + cos(z) = t
                val = math.cos(x_mm * freq) + math.cos(y_mm * freq) + math.cos(z_mm * freq)
                
                # Threshold for "Structure"
                if abs(val) < 0.5: # Iso-surface thickness
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    print("Extracting Mesh...")
    # Manual extraction
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_xy):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_xy):
                y_mm = (y * step) - (diameter/2)
                if not grid[x,y,z]: continue
                s2 = step/2
                
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/06_lattice/lattice_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)