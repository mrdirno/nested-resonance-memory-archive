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
# HELIOS LAMP SERIES 05: THE AETHER (SHADE)
# -----------------------------------------------------------------------------
# Logic: Quintessence / Void Structure.
# Method: Minimalist Lattice / Ethereal Web.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE AETHER SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Aether Logic
    # Almost invisible structure.
    # Very thin Gyroid struts?
    # Or Point Cloud structure (connected by thin lines)?
    
    # Let's use "Atom" logic.
    # Spheres connected by cylinders.
    # Or "Constellation"
    
    scale = 2.0 * math.pi / 30.0
    
    print("Simulating Quintessence...")
    
    radius = diameter / 2.0
    
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

                # --- PRIORITY 3: AETHER SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Structure
                # High frequency lattice, very thin
                # sin(x) * sin(y) * sin(z)
                # Threshold very small for thin lines
                
                # Rotate to avoid alignment artifacts
                # 4D rotation? No, just simple rotation
                
                # P (Primitive) Surface
                val = math.cos(x_mm*scale) + math.cos(y_mm*scale) + math.cos(z_mm*scale)
                
                # Range -3 to 3
                # Struts are at val approx 0
                
                thickness = 0.3
                if abs(val) < thickness:
                    # Add Nodes at intersections?
                    # Intersection is where 2 cosines cancel out?
                    # Let's just use the lattice
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    # Add random floating particles (quintessence)
                    # Dust motes
                    if (x_idx * y_idx * z_idx) % 10000 == 0:
                         grid[x_idx,y_idx,z_idx] = True # Single voxel
                    else:
                         grid[x_idx,y_idx,z_idx] = False
                         
                # Ensure Hand Access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "aether_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
