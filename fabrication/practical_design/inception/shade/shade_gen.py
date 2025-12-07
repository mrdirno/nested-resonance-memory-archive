import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.5 (BED MAXIMIZED)
# -----------------------------------------------------------------------------
# Correction Cycle 2846:
# - User Feedback: "Slightly smaller waves... brim 3/4 inch... expand width 1 inch...
#   extend wave to top (flat)... missing corner links (outline)... maximize bed."
# - Geometry:
#   - Base Width: 194mm + 25.4mm = 219.4mm (Max Ender 3 Bed Width).
#   - Top Width: 85.4mm + 25.4mm = 110.8mm (Proportional expansion).
#   - Height: 217.65mm.
#   - Wall Bottom: 19.05mm (3/4 inch).
#   - Wall Top: 6.35mm (1/4 inch).
# - Logic:
#   - Inverted Flow (Confirmed).
#   - Wave Scale: Base/2.8 (Slightly smaller than Base/2.5).
#   - Corners: SOLID (Pyramid Outline).
#   - Top: PATTERNED (Not solid block, "linking sides").
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=219.4, top_width=110.8, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.5 (Bed Maximized): {output_path}")
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
    # "Slightly smaller waves" than Base/2.5.
    # Let's use Base/2.8.
    base_scale = 2.0 * math.pi / (base_width / 2.8)
    
    print("Calculating Field (Inverted Flow + Corners)...")
    
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
                
                # --- TOP PLATE (Patterned) ---
                # "Extend wave design meeting to the top... keep it flat"
                # We use the pattern, but enforce the flat disk shape (with hole).
                # Top 4mm.
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    
                    # Keep it within the top dimensions
                    if abs(x_mm) < current_half_width and abs(y_mm) < current_half_width:
                        # Apply Pattern Check (instead of forcing True)
                        # We want "linking all sides".
                        # Let's use a thicker threshold for the top plate to ensure connectivity.
                        
                        val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                              math.sin(y_mm * base_scale) * math.cos(z_prime * base_scale) + \
                              math.sin(z_prime * base_scale) * math.cos(x_mm * base_scale)
                        
                        # Solidify Corners of the top plate for strength?
                        # User said "linking all sides".
                        # Let's use a high threshold (0.7) to make it mostly solid but patterned.
                        if abs(val) < 0.7:
                            grid[x_idx,y_idx,z_idx] = True
                        
                        continue
                
                # --- BOTTOM RIM ---
                if z_mm < 4.0:
                    # Solid Rim for structure
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- CORNER LINKS (Pyramid Outline) ---
                # "Outline the pyramid"
                # Solid vertical rails at the 4 corners.
                edge_thickness = 6.0 # Visible outline
                in_x_edge = abs(x_mm) > (current_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_half_width - edge_thickness)
                
                if in_x_edge and in_y_edge:
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
