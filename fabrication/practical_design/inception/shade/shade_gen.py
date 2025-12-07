import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EXPANSION SHADE v2.4 (BIG BANG REVISION)
# -----------------------------------------------------------------------------
# Correction Cycle 2833:
# - Logic: "Big Bang" Expansion (Small Waves at Top -> Large Waves at Bottom).
# - Physics: "Expanding down and out".
# - Breathability: NO SOLID BARRIER/SKIN. Open lattice structure.
# - Geometry: V2.4 (Height 217.65mm, Top 85.4mm, Base 194mm).
# - Twist: Slight "Space Time" twist.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating EXPANSION SHADE v2.4 (No Barrier): {output_path}")
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
    
    # FREQUENCY GRADIENT (The Big Bang)
    # Top = Early Universe = High Density = Small Wavelength
    # Bottom = Expanded Universe = Low Density = Large Wavelength
    
    wavelength_top = 35.0  # Small waves
    wavelength_bottom = 75.0 # Large waves (Expanding out)
    
    scale_top = 2.0 * math.pi / wavelength_top
    scale_bottom = 2.0 * math.pi / wavelength_bottom
    
    print(f"Gradient: Top Wave={wavelength_top}mm -> Bottom Wave={wavelength_bottom}mm")
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # 1. Geometry (Frustum)
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # 2. Frequency Interpolation (Linear Z)
        current_scale = scale_bottom * (1.0 - z_norm) + scale_top * z_norm
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY CHECKS
                # Outer Box
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SOLID CAP (Mount) ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= 7.0:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(x_mm) < current_outer_half_width and abs(y_mm) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < 4.0:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 3: CORNERS ---
                # Keep corners solid for structural integrity
                edge_thickness = 5.0
                in_x_edge = abs(x_mm) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_outer_half_width - edge_thickness)
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 4: BODY (Breathable) ---
                
                # INNER VOID (Hollow Center)
                # Crucial: We Keep the Void, but we DO NOT add a solid skin around it.
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # NO BARRIER / NO INNER SKIN CODE HERE
                
                # PATTERN GENERATION
                # No Twist
                tx = x_mm
                ty = y_mm
                
                # Gyroid
                val = math.sin(tx * current_scale) * math.cos(ty * current_scale) + \
                      math.sin(ty * current_scale) * math.cos(z_mm * current_scale) + \
                      math.sin(z_mm * current_scale) * math.cos(tx * current_scale)
                      
                # Thickness Threshold
                # Slightly thicker at bottom for strength? No, standard is fine.
                is_solid = abs(val) < 0.55 
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Mesh
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
