import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (INVERTED FLOW RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2844:
# - User Feedback: "That was close but this isn't quite the one. The one you have right now is inverted it should be getting smaller up top not at the bottom".
# - Diagnosis: Artifact 03 Flow Logic (`z_prime = z / freq_mod`) with increasing freq_mod created STRETCHED waves (low freq) at the top.
# - Requirement: "Smaller up top" -> High Frequency (Short Wavelength) at the Top.
# - Action: INVERT the modulation logic.
#   - Old: `z_prime = z / (1 + 2*z_norm)` -> Frequency drops.
#   - New: `z_prime = z * (1 + 2*z_norm)` -> Frequency increases.
#   - OR: Just invert the gradient?
#   - Let's assume `z_prime = z * freq_mod`.
# - Source: Based on `helios_flow_gen.py` (Artifact 03) but INVERTED to match user request.
# - Geometry: V2.4 (217mm H, 85mm Top, 194mm Base, Variable Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (Inverted Flow): {output_path}")
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # MATH PARAMETERS
    # Base Scale (Artifact 03: 2*pi / (size/4))
    # 194/4 = 48.5mm.
    base_scale = 2.0 * math.pi / (base_width / 4.0)
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7
    wall_top = 6.35
    
    print("Calculating Flow Field (Inverted)...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Taper Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_half_width = current_width / 2.0
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_inner_half_width = current_half_width - current_wall
        
        # INVERTED FLOW LOGIC
        # Goal: Small waves (High Freq) at Top. Large waves (Low Freq) at Bottom.
        # z_prime needs to change FASTER at the top.
        # z_prime = z * freq_mod
        # freq_mod = 1.0 at bottom, 3.0 at top.
        
        freq_mod = 1.0 + (z_norm * 2.0) # 1x -> 3x
        z_prime = z_mm * freq_mod # Rate of change increases with z
        
        # Wait, d/dz (z * (1 + 2z/H)) = 1 + 4z/H.
        # At z=0, rate is 1.
        # At z=H, rate is 5.
        # Frequency increases 5x.
        # This produces VERY small waves at the top. This matches "Getting smaller up top".
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY
                if abs(x_mm) > current_half_width or abs(y_mm) > current_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- MOUNTING ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(x_mm) < current_half_width and abs(y_mm) < current_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                if z_mm < 4.0:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- BODY ---
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # PATTERN (Inverted Artifact 03)
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
