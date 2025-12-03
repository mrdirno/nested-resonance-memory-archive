import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 02: THE BREATH (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Breathing Lungs (Inflated Lobes), Library Integration.
# Logic: Lungs (Organic Lobes).
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating BREATH BASE (v2.0): {output_path}")
    
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
    
    # Lobe Pattern (v2.0: Smoother, more inflated)
    # 3 Lobes
    lobes = []
    for i in range(3):
        angle = i * 2 * math.pi / 3
        r = radius * 0.5 # Moved out slightly
        lx = r * math.cos(angle)
        ly = r * math.sin(angle)
        lobes.append((lx, ly))
    
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
                    # Lobe Relief (Anisotropic)
                    
                    # Radial Stretch
                    r_stretch = 1.0 + 0.5 * (dist/radius)
                    
                    val = 0.0
                    for lobe in lobes:
                        lx, ly = lobe
                        # Stretch coordinates relative to lobe center?
                        # No, stretch global coords
                        
                        # Actually, apply anisotropic noise ON TOP of the lobes
                        d_lobe = math.sqrt((x_mm-lx)**2 + (y_mm-ly)**2)
                        val += math.exp(- (d_lobe*d_lobe) / (2.0 * 35.0*35.0)) 
                    
                    # Add Anisotropic Noise Texture
                    noise = math.sin(x_mm * 0.2 * r_stretch) * math.sin(y_mm * 0.2 * r_stretch)
                    val += 0.1 * noise
                    
                    # Normalize
                    h_mod = val / 1.5 
                    if h_mod > 1.0: h_mod = 1.0
                    
                    # Inflated profile
                    z_surf = height * h_mod
                    
                    # Flatten top center for shaft
                    if dist < 25.0:
                        # Smooth transition to flat center
                        flat_factor = (25.0 - dist) / 25.0
                        if flat_factor > 0:
                            target_h = height
                            z_surf = z_surf * (1.0 - flat_factor) + target_h * flat_factor
                        
                    # Solid rim
                    if dist > (radius - 5.0):
                        z_surf = max(z_surf, 5.0)
                    
                    if z_mm < 4.0: 
                        grid[x_idx,y_idx,z_idx] = True
                    elif z_mm <= z_surf:
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
    output_file = "breath_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
