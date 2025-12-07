import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (SHADE) v2.4 - INCEPTION REVISION
# -----------------------------------------------------------------------------
# Based on: Redshift v2.0 (The "Original" v2)
# Adjustments (Cycle 2828/2831):
# 1. Height Reduced: 224mm -> 217.65mm (-1/4 inch).
# 2. Top Width Increased: 60mm -> 85.4mm (+1 inch).
# 3. Variable Wall Thickness: 1/2" (12.7mm) Bottom -> 1/4" (6.35mm) Top.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating REDSHIFT SHADE v2.4 (Inception): {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")

    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7 # 1/2 inch
    wall_top = 6.35    # 1/4 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Frequency (Redshift v2.0 Standard)
    base_scale = 2.0 * math.pi / (base_width / 6.0)
    
    print("Calculating Field (Redshift v2.4)...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # Square Frustum Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        
        # Variable Wall Thickness Interpolation
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Scale factor
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        # Anisotropic Z scale (Redshift Effect)
        current_scale_z = base_scale / (1.0 + 1.0 * z_norm)
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Global Bound
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- PRIORITY 1: ROBUST SOLID CAP ---
                if z_mm > (height - 4.0):
                    # Hole
                    if dist_from_center <= 7.0:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    # Solid Plate (Square)
                    if abs(x_mm) < current_outer_half_width and abs(y_mm) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # 3. Bottom Rim (Solid Frame)
                if z_mm < 4.0:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False # Inside
                    else:
                        grid[x_idx,y_idx,z_idx] = True # Rim
                    continue
                
                # 4. Reinforcing Corners (Solid Edges)
                edge_thickness = 5.0
                in_x_edge = abs(x_mm) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_outer_half_width - edge_thickness)
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 5. Body (Redshift Logic)
                # INNER VOID
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # INNER SKIN (Connectivity Anchor) - 2mm Solid Wall
                if abs(x_mm) < (current_inner_half_width + 2.0) and abs(y_mm) < (current_inner_half_width + 2.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # REDSHIFT HYPER-SHIFT PATTERN
                # Z-Warping
                z_warped = z_mm * (1.0 + z_norm)
                
                sx = scale_factor * base_scale
                sy = scale_factor * base_scale
                sz = base_scale
                
                val = math.sin(x_mm * sx) * math.cos(y_mm * sy) + \
                      math.sin(y_mm * sy) * math.cos(z_warped * sz) + \
                      math.sin(z_warped * sz) * math.cos(x_mm * sx)
                
                is_lattice = abs(val) < 0.55
                
                # SPIRAL RIBS
                angle = math.atan2(y_mm, x_mm)
                twist = z_norm * math.pi
                rib_phase = math.cos(6.0 * angle + twist)
                is_rib = rib_phase > 0.8
                
                if is_lattice or is_rib:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)