import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (SHADE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Enhanced Anisotropy, Higher Resolution, Strict Wall Thickness.
# Logic: Anisotropic Gyroid Frustum (Square Pyramid)
# Dims: 194mm Base -> 60mm Top -> 224mm Height
# Mount: SPIDER FITTER (Hub + Spokes), Hand Access.
# Wall: 1 Inch Thick (25.4mm)
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=60.0, height=224.0, resolution=150, hole_diameter=14.0):
    print(f"Generating THE VOID SHADE (Redshift v2.0): {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")
    
    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # 40mm Hub
    spoke_width = 8.0 
    top_plate_height = 4.0
    
    solid_rim_height = 4.0
    wall_thickness = 25.4 # 1 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Frequency (Refined for v2.0)
    # Higher base frequency for more intricate detail
    base_scale = 2.0 * math.pi / (base_width / 6.0) 
    k_mod = 0.8 # Stronger anisotropy
    
    print("Calculating Field (v2.0)...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Square Frustum Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - wall_thickness
        
        # Scale factor for coordinate mapping
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        # Anisotropic Z scale (Redshift Effect)
        current_scale_z = base_scale / (1.0 + k_mod * z_norm)
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Global Bound
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                # 2. Spider Fitter (Library Call)
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_from_center,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_outer_half_width
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue
                
                # 3. Bottom Rim (Solid Frame)
                if z_mm < solid_rim_height:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 4. Reinforcing Corners (Solid Edges)
                edge_thickness = 5.0
                in_x_edge = abs(x_mm) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_outer_half_width - edge_thickness)
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # 5. Body (Gyroid)
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                lx = x_mm * scale_factor
                ly = y_mm * scale_factor
                lz = z_mm
                
                val = math.sin(lx * base_scale) * math.cos(ly * base_scale) + \
                      math.sin(ly * base_scale) * math.cos(lz * current_scale_z) + \
                      math.sin(lz * current_scale_z) * math.cos(lx * base_scale)
                
                if abs(val) < 0.4:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction (Library)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "redshift_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)