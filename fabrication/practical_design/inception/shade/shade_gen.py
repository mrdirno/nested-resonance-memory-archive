import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.5 (FINAL DIMENSION TUNING)
# -----------------------------------------------------------------------------
# Correction Cycle 2847:
# - User Feedback:
#   1. "Reduce 1/2 inch all the way around" -> Base Width 219.4 - 25.4 = 194.0mm.
#   2. "Height max minus 1 inch" -> Ender 3 Max 250 - 25.4 = ~224mm.
#   3. "Create middle hole" -> Confirmed (14mm).
#   4. "Waves 10% smaller" -> Scale Base/2.8 -> Base/3.1.
#   5. "Outline top of pyramid" -> Added Solid Top Rim.
# - Geometry:
#   - Base: 194.0mm.
#   - Top: 85.4mm (Proportional).
#   - Height: 224.0mm.
#   - Wall: 3/4" (19.05mm) Bottom -> 1/4" (6.35mm) Top.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=224.0, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.5 (Final Tuning): {output_path}")
    print(f"Dims: {base_width:.1f} -> {top_width:.1f} x {height:.1f}mm")

    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0
    
    # Wall Thickness (Variable)
    wall_bottom = 19.05 # 3/4 inch
    wall_top = 6.35     # 1/4 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # MATH PARAMETERS
    # "Waves 10% smaller".
    # Previous: Base/2.8.
    # New: Base/3.1.
    base_scale = 2.0 * math.pi / (base_width / 3.1)
    
    print("Calculating Field (Inverted Flow + Full Outline)...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Taper Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_half_width = current_width / 2.0
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_inner_half_width = current_half_width - current_wall
        
        # INVERTED FLOW LOGIC
        freq_mod = 1.0 + (z_norm * 2.0) # 1x -> 3x
        z_prime = z_mm * freq_mod
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY
                if abs(x_mm) > current_half_width or abs(y_mm) > current_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- TOP PLATE (Patterned + Outline + Hole) ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False # Hole
                        continue
                    
                    # TOP RIM OUTLINE
                    edge_thickness_top = 6.0
                    in_x_edge_top = abs(x_mm) > (current_half_width - edge_thickness_top)
                    in_y_edge_top = abs(y_mm) > (current_half_width - edge_thickness_top)
                    if in_x_edge_top or in_y_edge_top: # OR for the square ring
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Patterned Plate Body
                    if abs(x_mm) < current_half_width and abs(y_mm) < current_half_width:
                        val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                              math.sin(y_mm * base_scale) * math.cos(z_prime * base_scale) + \
                              math.sin(z_prime * base_scale) * math.cos(x_mm * base_scale)
                        if abs(val) < 0.7: # Thick
                            grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # --- BOTTOM RIM ---
                if z_mm < 4.0:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- CORNER LINKS (Side Outline) ---
                edge_thickness = 6.0
                in_x_edge = abs(x_mm) > (current_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_half_width - edge_thickness)
                
                if in_x_edge and in_y_edge: # AND for the 4 vertical pillars
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- BODY ---
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # PATTERN (Inverted Flow)
                val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                      math.sin(y_mm * base_scale) * math.cos(z_prime * base_scale) + \
                      math.sin(z_prime * base_scale) * math.cos(x_mm * base_scale)
                      
                if abs(val) < 0.5:
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