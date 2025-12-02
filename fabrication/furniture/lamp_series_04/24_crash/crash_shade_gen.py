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

                # --- PRIORITY 3: CRASH SHELL ---
                
                # Bounds are loose due to explosion
                if dist_xy > (radius + 20.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Shard logic
                # Which shard is this voxel part of?
                # Nearest Voronoi center (original pos)
                
                # But we render the shard at its DISPLACED pos.
                # This is inverse mapping.
                # For a point P, find which shard S would land on P.
                # P = S_pos + S_disp
                # So we check if P is inside geometry defined by S.
                
                # Simplified:
                # Just evaluate noise field.
                # "Exploded" look = High frequency Worley noise with gaps.
                
                # 3D Worley (Voronoi) Noise
                # d1, d2
                # if d2-d1 < gap: Empty (Cracks)
                
                # To simulate explosion, we scale the coordinates away from center?
                # P_in = P_out * (1.0 - explosion_factor)
                
                # Radial explosion
                expl_factor = 0.8 # Compress space -> Expands object
                
                x_in = x_mm * expl_factor
                y_in = y_mm * expl_factor
                z_in = z_mm 
                
                # Evaluate base cylinder shape at x_in
                d_in = math.sqrt(x_in**2 + y_in**2)
                
                # Base shell exists?
                in_shell = False
                if d_in < radius and d_in > (radius - wall_thickness):
                    in_shell = True
                    
                if not in_shell:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Cracks
                # Voronoi basis
                # Random points in 3D
                # If close to edge, remove.
                
                # Simple pseudo-random check based on large blocks
                bx = math.floor(x_in / 20.0)
                by = math.floor(y_in / 20.0)
                bz = math.floor(z_in / 20.0)
                
                # Random displacement for this block
                # hash(bx,by,bz)
                seed = bx*31 + by*17 + bz*5
                dx = math.sin(seed)*5.0
                dy = math.cos(seed)*5.0
                
                # Check if current point is within the shifted block volume
                # Actually, simpler: Just add noise holes.
                
                # Use Gyroid but with sharp cuts
                scale = 2.0 * math.pi / 25.0
                val = math.sin(x_in*scale) + math.sin(y_in*scale) + math.sin(z_in*scale)
                
                if val > 0.5: # Large chunks missing
                    grid[x_idx,y_idx,z_idx] = False
                else:
                    # Add debris
                    # Small floating bits
                    if (x_idx+y_idx+z_idx) % 7 == 0:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                        
                # Ensure Hand Access (Final check)
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "crash_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
