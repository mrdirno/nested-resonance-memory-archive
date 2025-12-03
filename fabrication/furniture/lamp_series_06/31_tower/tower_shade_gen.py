import numpy as np
import math
import sys
import struct
import os
import random

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE TOWER (SHADE)
# -----------------------------------------------------------------------------
# Logic: Skyscraper / Art Deco (Vertical Ribs).
# Method: Polar coordinates with stepping radius (Setbacks).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE TOWER SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Art Deco Logic
    # 1. Vertical Ribs (Cosine on angle)
    # 2. Setbacks (Radius decreases in steps along Z)
    
    num_ribs = 16
    
    print("Constructing Edifice...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Setbacks logic
        # Step down radius at certain heights
        
        # Base radius
        current_base_r = radius
        
        if z_norm > 0.3: current_base_r *= 0.9
        if z_norm > 0.6: current_base_r *= 0.85 # cumulative: 0.9*0.85 = 0.765
        if z_norm > 0.85: current_base_r *= 0.8 # cumulative: 0.61
        
        # Add chamfer at setback transitions?
        # Let's keep it sharp for Brutalism/Deco feel.
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SPIDER FITTER ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: TOWER SHELL ---
                
                if dist_xy > (radius + 5.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Ribs
                angle = math.atan2(y_mm, x_mm)
                
                # Rib shape: Square wave or Cosine?
                # Art Deco uses sharp lines.
                # Square wave with smoothed corners?
                # Let's use: r = base + rib_depth * (cos(N*theta))^p (p < 1 makes it squarish)
                
                # Simple cosine ribs
                rib_val = math.cos(num_ribs * angle)
                
                # Make ribs positive only (additive)
                rib_ext = 5.0 * ((rib_val + 1.0) / 2.0)
                
                r_surf = current_base_r - 5.0 + rib_ext # Base is slightly recessed
                
                # Thickness
                # Inner wall smooth or ribbed?
                # Smooth inner wall for light diffusion
                
                if dist_xy <= r_surf and dist_xy >= (r_surf - wall_thickness):
                    # Add window slits?
                    # Vertical slits between ribs
                    
                    # Check if we are in a "valley" between ribs
                    if rib_val < -0.5:
                        # Valley
                        # Add windows
                        # Window pattern in Z
                        win_h = 10.0
                        win_gap = 5.0
                        if (z_mm % (win_h + win_gap)) < win_h:
                            # Window = Hole
                            # But only if thickness allows.
                            # We want translucent, not transparent?
                            # No, physical holes for light shafts.
                            
                            # Check depth. Only cut if we are deep in the wall?
                            # Let's cut through.
                            grid[x_idx,y_idx,z_idx] = False
                        else:
                            grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False
                    
                # Ensure Hand Access
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "tower_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
