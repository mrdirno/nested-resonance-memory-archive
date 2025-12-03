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
# HELIOS LAMP SERIES 04: THE GLITCH (BASE)
# -----------------------------------------------------------------------------
# Logic: Corrupted Foundation.
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Shifted blocks / Artifacts.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating GLITCH BASE: {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 # 14mm
    foot_radius = 10.0
    foot_depth = 3.0
    foot_offset = 15.0
    channel_height = 8.0
    channel_width = 8.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Glitch Pattern
    # Random Rectangular extrusions/intrusions
    num_blocks = 20
    blocks = []
    random.seed(404)
    
    for _ in range(num_blocks):
        w = random.uniform(10, 40)
        h = random.uniform(10, 40)
        x = random.uniform(-radius, radius)
        y = random.uniform(-radius, radius)
        depth = random.uniform(-5, 5)
        blocks.append((x, y, w, h, depth))
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Features
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist,
                    height=height,
                    hole_radius=rod_radius,
                    channel_height=channel_height,
                    channel_width=channel_width,
                    foot_depth=foot_depth,
                    foot_radius=foot_radius,
                    foot_offset=foot_offset,
                    radius=radius
                )
                
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue
                
                # Base Body
                if dist <= radius:
                    # Glitch Logic (v2.0)
                    # Horizontal Bands + XY Displacement
                    
                    # Anisotropy: Shearing layers
                    
                    # Define shift per layer
                    shift_x = 0.0
                    shift_y = 0.0
                    
                    # Layer height 5mm
                    layer_idx = int(z_mm / 5.0)
                    
                    # Deterministic pseudo-random based on layer
                    random.seed(layer_idx + 55)
                    if random.random() > 0.5:
                        shift_x = random.uniform(-3.0, 3.0)
                        shift_y = random.uniform(-3.0, 3.0)
                        
                    # Apply shift
                    sx = x_mm - shift_x
                    sy = y_mm - shift_y
                    
                    s_dist = math.sqrt(sx**2 + sy**2)
                    
                    # CONNECTIVITY CORE (Spine)
                    # Ensure center 15mm is solid and unshifted
                    if dist < 15.0:
                        sx = x_mm
                        sy = y_mm
                        s_dist = dist
                    
                    # Boxy or Round?
                    # Let's do Round but shifted
                    
                    z_surf = height
                    if s_dist > (radius - 5.0):
                        z_surf = height - 5.0 # Step down
                        
                    # Solid Rim (Unshifted for stability)
                    if dist > (radius - 2.0): 
                        z_surf = height
                        sx = x_mm # Reset shift for rim
                        sy = y_mm
                        
                    # Bottom solid
                    if z_mm < 4.0:
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
                        # Cutout noise?
                        is_noise = False
                        if random.random() > 0.95:
                            is_noise = True
                            
                        # Protect Core
                        if dist < 15.0: is_noise = False
                        
                        if is_noise:
                            grid[x_idx,y_idx,z_idx] = False
                        else:
                            grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "glitch_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
