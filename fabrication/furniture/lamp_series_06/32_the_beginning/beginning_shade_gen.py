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
# HELIOS LAMP SERIES 06: THE BEGINNING (SHADE)
# -----------------------------------------------------------------------------
# Logic: The Big Bang (Explosion/Expansion).
# Method: Radial Explosion Vectors (Spikes/Shards).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE BEGINNING SHADE: {output_path}")
    
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
    
    # Explosion Logic
    # A series of spikes radiating from a central point (inside the lamp).
    # Center of explosion: (0,0, height/2)
    
    cx, cy, cz = 0.0, 0.0, height/2.0
    
    # Generate Shards/Spikes
    num_shards = 40
    shards = []
    random.seed(10101)
    
    for _ in range(num_shards):
        # Random direction
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        
        dx = math.sin(phi) * math.cos(theta)
        dy = math.sin(phi) * math.sin(theta)
        dz = math.cos(phi)
        
        # Thickness
        thick = random.uniform(4.0, 10.0)
        
        shards.append(((dx,dy,dz), thick))
    
    print("Creating Universe...")
    
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

                # --- PRIORITY 3: EXPLOSION SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Explosion Pattern
                # Check distance to nearest shard ray
                
                vec_x = x_mm - cx
                vec_y = y_mm - cy
                vec_z = z_mm - cz
                
                # Project point onto shard vector
                is_solid = False
                
                # Optimization: Check angle relative to center?
                # Or Voronoi on sphere?
                
                # Let's do explicit distance check to rays
                # Only check if point is far enough from center (in the shell wall)
                
                min_dist = 999.0
                
                for shard in shards:
                    d_vec, thick = shard
                    dx, dy, dz = d_vec
                    
                    # Dot product
                    t = vec_x*dx + vec_y*dy + vec_z*dz
                    
                    if t > 0: # In direction of shard
                        # Closest point on line
                        px = t * dx
                        py = t * dy
                        pz = t * dz
                        
                        dist_sq = (vec_x-px)**2 + (vec_y-py)**2 + (vec_z-pz)**2
                        
                        # Cone expansion? Shards get wider?
                        # Width = thick * (t / 100.0)?
                        width = thick * (1.0 + t/100.0)
                        
                        if dist_sq < (width*width):
                            is_solid = True
                            break
                            
                # Hand access override
                if dist_xy < hand_access_radius: is_solid = False
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "beginning_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
