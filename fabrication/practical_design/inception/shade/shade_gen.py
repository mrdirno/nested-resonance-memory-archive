import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (CORNERSTONE RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2837:
# - User Feedback: "Math/Design is wrong", "No Rim Outline (Pyramid)", "Alternating waves".
# - Diagnosis: The "Rim Outline" refers to SOLID CORNERS (Rails) which were present in Redshift but missing in Prism.
# - Logic Restoration:
#   1. PRISM MATH (Coordinate Scaling): Preserves the "Small Top / Large Bottom" logic without staircase.
#   2. REDSHIFT FEATURES: Added Solid Corners (Rim Outline) and Bottom Rim.
#   3. ANISOTROPY: Tuned to produce the "Alternating" visual (Z-stretch > 1.5).
# - Geometry: V2.4 (217.65mm H, 85.4mm Top, 194mm Base).
# - Wall: Variable 12.7mm -> 6.35mm.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (Corners + Expansion): {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")

    # Mount Parameters
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
    
    # MATH PARAMETERS
    # Large Waves: Base/3.5
    base_pattern_scale = 2.0 * math.pi / (base_width / 3.5)
    
    # Z Scale (Anisotropic Stretch)
    # To get "Alternating up/side", we need significant anisotropy.
    # Stretch Z by 1.5x to 2.0x
    base_scale_z = base_pattern_scale / 1.6
    
    # K Expansion (Taper)
    k_expansion = (top_width / base_width) - 1.0
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # 1. Taper Logic
        shape_scale_factor = 1.0 + k_expansion * z_norm
        current_width = base_width * shape_scale_factor
        
        # Variable Wall Logic
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Coordinate Scaling (The Big Bang)
        ratio = base_width / current_width
        
        for x_idx in range(res_xy):
            px_unscaled = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                py_unscaled = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY CHECKS
                if abs(px_unscaled) > current_outer_half_width or abs(py_unscaled) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(px_unscaled**2 + py_unscaled**2)
                
                # --- PRIORITY 1: SOLID CAP ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(px_unscaled) < current_outer_half_width and abs(py_unscaled) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < 4.0:
                    if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 3: SOLID CORNERS (RIM OUTLINE) ---
                # Reinforcing the pyramid edges
                edge_thickness = 5.0
                in_x_edge = abs(px_unscaled) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(py_unscaled) > (current_outer_half_width - edge_thickness)
                
                # If we are in the corner zone (both edges?) No, that's just the point.
                # We want the FRAME.
                # Frame = Near X edge OR Near Y edge? No, that's a box.
                # Frame = Corners (X and Y).
                # Wait, "Rim outline of the pyramid" usually means the 4 corners running up.
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 4: BODY ---
                if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # PATTERN GENERATION
                px = px_unscaled * ratio
                py = py_unscaled * ratio
                
                # Gyroid
                val = math.sin(px * base_pattern_scale) * math.cos(py * base_pattern_scale) + \
                      math.sin(py * base_pattern_scale) * math.cos(z_mm * base_scale_z) + \
                      math.sin(z_mm * base_scale_z) * math.cos(px * base_pattern_scale)
                      
                if abs(val) < 0.55:
                    grid[x_idx,y_idx,z_idx] = True

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Mesh
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)