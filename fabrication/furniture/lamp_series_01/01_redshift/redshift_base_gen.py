import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Refined Gradient Gyroid, Library Integration.
# Logic: Linear Gradient Gyroid (Density increases with radius).
# Features: V4 QA (Feet, Channel, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, 
                  diam=180.0,       # Diameter
                  height=25.0,      # Height (increased slightly for channel clearance)
                  resolution=100):
    
    print(f"Generating Redshift Base (v2.0): {output_path}")
    
    radius = diam / 2.0
    
    # Channel Config
    channel_width = 8.0 
    channel_height = 8.0
    
    # Feet Config
    foot_radius = 10.0
    foot_offset = 15.0 # V4 Std offset
    foot_depth = 3.0
    
    # Center Hole
    hole_radius = 7.0 # 14mm diam
    
    # Grid
    res_x = resolution
    res_y = resolution
    step_ref = diam / resolution
    res_z = int(height / step_ref)
    
    step_x = diam / res_x
    step_y = diam / res_y
    step_z = height / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_x:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Gyroid Params (Refined)
    scale = 2.0 * math.pi / (25.0) # 25mm wavelength (tighter)
    
    print("Calculating Field (v2.0)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        
        for x_idx in range(res_x):
            px = (x_idx * step_x) - radius
            
            for y_idx in range(res_y):
                py = (y_idx * step_y) - radius
                
                r = math.sqrt(px**2 + py**2)
                
                # V4 Features Check
                feature_check = lamp_lib.apply_base_v4_features(
                    px, py, pz, r,
                    height=height,
                    hole_radius=hole_radius,
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

                # 3. BASE BODY
                if r <= radius:
                    # Gradient Density Gyroid
                    # Threshold varies with radius? No, scale or threshold.
                    # Let's vary threshold to make it denser at center, airy at edge?
                    # Or solid rim.
                    
                    # Solid Rim
                    if (pz < 2.0) or (pz > height - 2.0) or (r > radius - 3.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Solid Core (Stability)
                    if r < 25.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Gyroid
                    # Hyper-Anisotropy: Stretch X/Y based on radius? No, Stretch Z.
                    # Let's apply a radial stretch factor.
                    
                    # Anisotropic Scale Factors
                    sx = scale * 1.0
                    sy = scale * 1.0
                    sz = scale * 0.5 # Stretched vertically (Lower freq = longer waves)
                    
                    # Radial Distortion (Swirl)
                    angle = math.atan2(py, px)
                    twist = r * 0.05
                    
                    tx = r * math.cos(angle + twist)
                    ty = r * math.sin(angle + twist)
                    
                    val = math.sin(tx * sx) * math.cos(ty * sy) + \
                          math.sin(ty * sy) * math.cos(pz * sz) + \
                          math.sin(pz * sz) * math.cos(tx * sx)
                          
                    # Gradient Threshold
                    # Center (r=25): Solid
                    # Edge (r=90): Airy (thresh 0.3)
                    
                    t_norm = (r - 25.0) / (radius - 25.0)
                    if t_norm < 0: t_norm = 0
                    if t_norm > 1: t_norm = 1
                    
                    threshold = 0.8 - (0.5 * t_norm) # 0.8 -> 0.3
                    
                    if abs(val) < threshold:
                        grid[x_idx, y_idx, z_idx] = True
                    else:
                        grid[x_idx, y_idx, z_idx] = False
                else:
                    grid[x_idx, y_idx, z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction (Library)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step_x, diam, diam)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "redshift_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)