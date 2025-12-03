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
                  height=25.0,      # Height
                  resolution=150):  # INCREASED RES
    
    print(f"Generating Redshift Base (v2.1 - High Visibility): {output_path}")
    
    radius = diam / 2.0
    
    # Channel Config
    channel_width = 8.0 
    channel_height = 8.0
    
    # Feet Config
    foot_radius = 10.0
    foot_offset = 15.0
    foot_depth = 3.0
    
    # Center Hole
    hole_radius = 7.0 
    
    # Grid
    res_x = resolution
    res_y = resolution
    step_ref = diam / resolution
    res_z = int(height / step_ref)
    
    step_x = diam / res_x
    step_y = diam / res_y
    step_z = height / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Gyroid Params
    scale = 2.0 * math.pi / 25.0
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        
        for x_idx in range(res_x):
            px = (x_idx * step_x) - radius
            
            for y_idx in range(res_y):
                py = (y_idx * step_y) - radius
                
                r = math.sqrt(px**2 + py**2)
                
                # V4 Features (Feet/Channel voids)
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
                    # NO SOLID RIM. Expose lattice to edge.
                    
                    # Anisotropic Doppler Vortex
                    sx = scale * 1.0
                    sy = scale * 1.0
                    sz = scale * 0.5 
                    
                    angle = math.atan2(py, px)
                    twist = r * 0.05 # Reduced twist for connectivity
                    
                    tx = r * math.cos(angle + twist)
                    ty = r * math.sin(angle + twist)
                    
                    lx = tx * sx
                    ly = ty * sy
                    lz = pz * sz
                    
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    is_lattice = abs(val) < 0.35
                    
                    # CONNECTIVITY RIB (Hidden Spoke)
                    # 4 Radial Spokes to bind the spirals
                    # Modulated by Z to be less intrusive
                    rib_angle = math.cos(4.0 * angle)
                    is_rib = rib_angle > 0.95 # Very thin ribs
                    
                    # Shell Logic (Rim and Bottom)
                    if pz < 2.0: # Solid Base Plate (Anchor)
                         grid[x_idx,y_idx,z_idx] = True
                    elif r < 12.0: # Mechanical Core
                         grid[x_idx,y_idx,z_idx] = True
                    else:
                         if is_lattice or is_rib:
                             grid[x_idx,y_idx,z_idx] = True
                         else:
                             grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction (Library)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step_x, diam, diam)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "redshift_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)