import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (ORIGINAL REVISION)
# -----------------------------------------------------------------------------
# Correction Cycle 2832:
# - User identified V2.0 Redshift introduced "Step/Staircase" artifacts.
# - User requests "Original Design" with "Much Larger Waves".
# - Implementation: Standard Gyroid (Anisotropic stretch in Z, no Hyper-Shift Z-Warp).
# - V2.4 Geometry: Height 217.65mm, Top 85.4mm, Base 194mm.
# - Variable Wall Thickness: 12.7mm -> 6.35mm.
# - Slight Twist: Applied to pattern coordinates only (not boundary).
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (Original Large Wave): {output_path}")
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
    
    # FREQUENCY SETUP (LARGE WAVES)
    # The user wanted "larger waves" than Redshift.
    # Redshift had ~32mm wavelength (base/6).
    # Lattice had 30mm wavelength.
    # To get "much larger", let's try 50-60mm wavelength.
    # Let's use Base/3.5 (~55mm).
    
    wavelength_xy = base_width / 3.5 
    scale_xy = 2.0 * math.pi / wavelength_xy
    
    # Anisotropy: Stretch Z (Lower frequency in Z)
    # Standard Anisotropic Gyroid is usually stretched 1.5x - 2x in Z.
    wavelength_z = wavelength_xy * 1.5
    scale_z = 2.0 * math.pi / wavelength_z
    
    print(f"Wave Scale: XY={wavelength_xy:.1f}mm, Z={wavelength_z:.1f}mm")
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # Square Frustum Logic (Boundary)
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        
        # Variable Wall Thickness Interpolation
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Coordinate Scaling for Pattern
        # To maintain pattern size relative to the *tapered* shape (if desired),
        # we would scale coordinates by (base_width / current_width).
        # However, usually "Original Design" implies the pattern is fixed in space 
        # and the shape cuts through it.
        # But users often like the pattern to "flow" with the taper.
        # Given "Redshift" tried to scale density, let's stick to "Fixed Pattern Space" 
        # or "Slightly Adaptive".
        # Let's use Fixed Pattern Space for "Clean Large Waves".
        # Wait, if we don't scale, the pattern gets cut off.
        # Let's apply the Slight Twist here.
        
        twist_angle = (z_norm * math.pi / 4.0) # 45 degree twist top to bottom (Slight)
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # 1. Global Bound Check (Untwisted / Unwarped)
                # This ensures the physical outline is a perfect Pyramid
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: ROBUST SOLID CAP ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= 7.0: # Hole
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
                edge_thickness = 5.0
                in_x_edge = abs(x_mm) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_outer_half_width - edge_thickness)
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 4: BODY ---
                # INNER VOID
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # INNER SKIN
                if abs(x_mm) < (current_inner_half_width + 2.0) and abs(y_mm) < (current_inner_half_width + 2.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # PATTERN GENERATION
                # Apply Twist to Coordinates used for Math
                # x_rot = x * cos - y * sin
                # y_rot = x * sin + y * cos
                
                ca = math.cos(twist_angle)
                sa = math.sin(twist_angle)
                
                tx = x_mm * ca - y_mm * sa
                ty = x_mm * sa + y_mm * ca
                
                # Gyroid Equation
                # sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x)
                
                val = math.sin(tx * scale_xy) * math.cos(ty * scale_xy) + \
                      math.sin(ty * scale_xy) * math.cos(z_mm * scale_z) + \
                      math.sin(z_mm * scale_z) * math.cos(tx * scale_xy)
                      
                is_solid = abs(val) < 0.6 # Thickness
                
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
