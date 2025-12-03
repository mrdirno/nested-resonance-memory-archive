import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE FUTURIST (SHADE)
# -----------------------------------------------------------------------------
# Logic: Aerodynamic Streamline.
# Method: Airfoil Sections (Wing profiles).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE FUTURIST SHADE: {output_path}")
    
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
    
    # Streamline Logic
    # Vertical Fins / Airfoils
    num_fins = 8
    
    # Twist
    twist_total = math.pi / 4.0 # Gentle twist
    
    print("Streamlining Future...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Twist
        angle_offset = z_norm * twist_total
        
        # Taper (Teardrop)
        # Wide top, narrow bottom? Or reverse?
        # Futurist usually implies speed -> Teardrop
        # Wide top (engine intake), narrow bottom (exhaust)
        
        current_radius = radius * (0.6 + 0.4 * math.sin(z_norm * math.pi))
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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

                # --- PRIORITY 3: STREAMLINE SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Inner void
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Fin Logic
                # Fin centers at N angles
                # Fin profile: Distance from radial line
                
                # Rotate point to align with first fin at 0
                local_angle = angle + angle_offset
                
                # Sectorize
                sector = 2*math.pi / num_fins
                a_quant = math.floor(local_angle / sector) * sector + (sector/2)
                d_fin_center = abs(angle - a_quant) # Angular distance? No.
                
                # Rotate point to local sector frame
                rot_sec = -a_quant
                rx = x_mm * math.cos(rot_sec) - y_mm * math.sin(rot_sec)
                ry = x_mm * math.sin(rot_sec) + y_mm * math.cos(rot_sec)
                
                # Now ry is distance from fin center line (if fin is along X)
                # Fin thickness
                fin_thickness = 6.0 * (1.0 - (dist_xy/radius)) + 2.0 # Taper out
                
                if abs(ry) < fin_thickness:
                    # Fin body
                    # Cut off inner/outer
                    if dist_xy < current_radius and dist_xy > hand_access_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Connect fins with a thin shell?
                # No, open fins are cooler. But we need structural integrity.
                # Let's add rings.
                
                ring_spacing = 30.0
                dist_to_ring = abs(z_mm % ring_spacing)
                if dist_to_ring < 2.0:
                     if dist_xy < current_radius and dist_xy > hand_access_radius:
                        grid[x_idx,y_idx,z_idx] = True

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "futurist_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
