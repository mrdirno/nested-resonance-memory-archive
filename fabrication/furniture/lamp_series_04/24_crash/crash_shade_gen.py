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
# HELIOS LAMP SERIES 04: THE CRASH (SHADE)
# -----------------------------------------------------------------------------
# Logic: Buffer Overflow / Explosion.
# Method: Displaced Shards (Voronoi or Triangle explosion) from center.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE CRASH SHADE (EXPLOSION): {output_path}")
    
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
    
    # Crash Logic
    # Define Shards: Random planes cutting space?
    # Or cellular explosion?
    
    # Let's use Voronoi cells again, but this time displace them outward based on Z height or randomness.
    # "Fragmented Mesh" look.
    
    num_shards = 40
    shards = []
    random.seed(404) # Error 404
    
    for _ in range(num_shards):
        # Center of shard
        r = random.uniform(0, diameter/2)
        theta = random.uniform(0, 2*math.pi)
        z = random.uniform(0, height)
        
        # Displacement vector (Explosion)
        dr = random.uniform(0, 20.0)
        dx = dr * math.cos(theta)
        dy = dr * math.sin(theta)
        dz = random.uniform(-10, 10)
        
        shards.append({
            'pos': (r*math.cos(theta), r*math.sin(theta), z),
            'disp': (dx, dy, dz)
        })
        
    print("Simulating Buffer Overflow...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: CRASH SHELL (Anisotropic Explosion) ---
                
                # Bounds are loose due to explosion
                if dist_xy > (radius + 20.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Anisotropy: Radial Explosion
                # Scale coords towards center
                
                expl_factor = 0.8 
                x_in = x_mm * expl_factor
                y_in = y_mm * expl_factor
                z_in = z_mm 
                
                d_in = math.sqrt(x_in**2 + y_in**2)
                
                in_shell = False
                if d_in < radius and d_in > (radius - wall_thickness):
                    in_shell = True
                    
                if not in_shell:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Cracks (Anisotropic)
                # Z-Stretched Noise
                
                scale = 2.0 * math.pi / 25.0
                sz = scale * 0.5 # Vertical fractures
                
                val = math.sin(x_in*scale) + math.sin(y_in*scale) + math.sin(z_in*sz)
                
                if val > 0.6: # Large chunks missing
                    grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = True
                        
                # Ensure Hand Access (Final check)
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "crash_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
