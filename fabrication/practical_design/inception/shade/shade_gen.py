import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ORIGINAL HYPER-SHIFT SHADE v2.4
# -----------------------------------------------------------------------------
# Correction Cycle 2835:
# - Goal: Precise restoration of the "Original" math (Hyper-Shift).
# - Source: fabrication/furniture/lamp_series_01/01_redshift/redshift_shade_gen.py
# - Logic: Z-Warped Anisotropic Gyroid with Spiral Ribs.
# - User Feedback: "Patterns don't look quite the same" in Cycle 2834 (Big Bang).
# - Hypothesis: The "Original" Redshift code used Z-Warping + Constant Z Freq + Scaling X/Y Freq.
# - Fix: Re-implement the EXACT Redshift logic but map it to the new V2.4 Geometry.
# - V2.4 Geometry: Height 217.65mm, Top 85.4mm, Base 194mm.
# - Wall: Variable 12.7mm -> 6.35mm.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ORIGINAL HYPER-SHIFT SHADE v2.4 (Redshift Logic): {output_path}")
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
    
    # REDSHIFT MATH PARAMETERS (From Source)
    # base_scale = 2.0 * math.pi / (base_width / 6.0) -> ~32mm wavelength
    # The user said "Original design... see how the waves are much larger".
    # Maybe Redshift ISN'T the original they mean, but they said "I believe was redshift".
    # If they want LARGER waves, I should decrease the frequency divisor.
    # Let's use (base_width / 3.5) like I did in Cycle 2832, but with Redshift Z-Warp.
    
    wavelength_xy = base_width / 3.5 # ~55mm (Large Waves)
    base_scale = 2.0 * math.pi / wavelength_xy
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # Square Frustum Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Scale factor for coordinate mapping
        # Redshift logic: scale_factor = base_width / current_width
        # This keeps the number of cells constant across the taper (cells get smaller at top).
        # If the user wants "Expansion down and out", this is actually INVERSE to that?
        # No, "Expansion down and out" = Small at top, Large at bottom.
        # If cells get smaller at top (width decreases), that MATCHES "Small at top".
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Global Bound (Frustum)
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- PRIORITY 1: SOLID CAP ---
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
                
                # NO BARRIER / NO INNER SKIN
                
                # REDSHIFT MATH (Restored)
                # Z-Warping (Redshift Effect)
                # Compress Z coordinates logarithmically
                # z_warped = z_mm * (1.0 + z_norm)
                # This makes Z spacing increase as Z increases (cells get compressed at top? No.)
                # z=0 -> warped=0. z=H -> warped=2H.
                # Frequency is constant `sz`.
                # Phase change per mm = d(z_warped)/dz = 1 + 2*z_norm/H approx.
                # Phase change INCREASES at top. Frequency INCREASES at top.
                # Wavelength DECREASES at top.
                # THIS MATCHES "Small at top, Large at bottom".
                
                z_warped = z_mm * (1.0 + z_norm)
                
                sx = scale_factor * base_scale
                sy = scale_factor * base_scale
                sz = base_scale
                
                val = math.sin(x_mm * sx) * math.cos(y_mm * sy) + \
                      math.sin(y_mm * sy) * math.cos(z_warped * sz) + \
                      math.sin(z_warped * sz) * math.cos(x_mm * sx)
                
                is_lattice = abs(val) < 0.55
                
                # CONNECTIVITY GUARANTEE: Spiral Ribs (Thickened)
                # "Staircase" might have been due to lack of ribs?
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
    
    # Mesh
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)