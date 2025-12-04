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
                
                # --- PRIORITY 1: MOUNT (Cantilever Bar/Ring) ---
                if z_mm > (height - 6.0): # Top 6mm
                    # Central Hub (Solid)
                    if dist_xy < 22.0 and dist_xy > 7.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    # Hole
                    if dist_xy <= 7.0:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # Cantilever Bars (Spokes)
                    spoke_angle = math.atan2(y_mm, x_mm)
                    if math.cos(3.0 * spoke_angle) > 0.9: 
                         if dist_xy < radius:
                             grid[x_idx,y_idx,z_idx] = True
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
                # Anisotropy: Z-Twisted Fins
                
                local_angle = angle + angle_offset
                
                # Sectorize
                sector = 2*math.pi / num_fins
                
                # Normalize angle to sector
                # dist from center of nearest sector
                a_norm = (local_angle % sector)
                if a_norm > (sector/2): a_norm -= sector
                
                # Angular distance
                d_ang = abs(a_norm) * dist_xy # Arc length approx
                
                fin_thickness = 4.0 
                
                if d_ang < (fin_thickness / 2.0):
                    if dist_xy < current_radius:
                        grid[x_idx,y_idx,z_idx] = True
                
                # CONNECTIVITY RINGS
                # Rings every 30mm to hold fins together
                ring_spacing = 30.0
                if (z_mm % ring_spacing) < 3.0:
                     if dist_xy < current_radius and dist_xy > hand_access_radius:
                        grid[x_idx,y_idx,z_idx] = True

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "futurist_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
