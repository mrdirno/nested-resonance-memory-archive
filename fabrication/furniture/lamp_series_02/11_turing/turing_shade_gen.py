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
    wall_thickness = 25.4 # 1 inch
    hand_access_radius = 45.0 # 90mm internal clearance
    
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
                
                # --- PRIORITY 1: SPIDER FITTER ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: SHELL BODY ---
                
                # Shell Definition: Simple Cylinder with rounded top
                # Or straight cylinder for "Petri Dish" look?
                # Let's do straight cylinder to maximize pattern visibility.
                
                # Inner/Outer bounds
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Turing Pattern Logic
                # f(x,y,z) = sin(s1*x)*sin(s1*y)*sin(s1*z) + ...
                # This is closer to gyroid.
                
                # Better Turing Approx: 
                # val = abs(sin(x) + sin(y) + sin(z)) - width
                # But we want the "worm" look.
                # "Worm" look comes from band-passing noise.
                # Abs(SimplexNoise) is good.
                # Let's stick to a deterministic math function that looks like worms.
                # Swift-Hohenberg equation approximation?
                
                # Try: sin(x) * sin(y) * sin(z) + sin(x*k)*cos(y*k) ...
                
                v1 = math.sin(x_mm * scale_1) + math.sin(y_mm * scale_1) + math.sin(z_mm * scale_1)
                v2 = math.cos(x_mm * scale_2) * math.cos(y_mm * scale_2) * math.cos(z_mm * scale_2)
                
                # Mixing
                val = v1 + 0.5 * v2
                
                # Turing spots/stripes usually emerge at specific threshold bands
                # e.g. -0.2 < val < 0.2
                
                if abs(val) < 0.5:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "turing_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
