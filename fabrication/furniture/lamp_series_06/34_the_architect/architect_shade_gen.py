import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE ARCHITECT (SHADE)
# -----------------------------------------------------------------------------
# Logic: The Blueprint (Construction Lines).
# Method: Wireframe Grid / Structural Beams.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE ARCHITECT SHADE: {output_path}")
    
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
    
    # Blueprint Logic
    # A grid of thin lines defining a shape.
    # Shape: A truncated cone or cylinder with a dome.
    
    print("Drafting Plans...")
    
    radius = diameter / 2.0
    
    # Grid lines
    num_verticals = 12
    num_horizontals = 8
    
    beam_thick = 3.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
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

                # --- PRIORITY 3: ARCHITECT SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Blueprint Grid
                # Vertical beams
                # cos(N*theta) > threshold
                
                # Cosine for beam profile width ~ 3mm
                # At radius 100, circum = 628.
                # 12 beams -> spacing 52mm.
                # 3mm width -> 3/52 fraction -> narrow pulse.
                
                # Just use angular distance
                sector = 2*math.pi/num_verticals
                angle_dist = min(abs(angle % sector), abs(sector - (angle % sector)))
                
                # Convert angle dist to arc length
                arc_dist = angle_dist * dist_xy
                
                is_vert = arc_dist < (beam_thick/2.0)
                
                # Horizontal beams
                # z % spacing
                h_spacing = height / num_horizontals
                z_dist = min(abs(z_mm % h_spacing), abs(h_spacing - (z_mm % h_spacing)))
                
                is_horz = z_dist < (beam_thick/2.0)
                
                # Diagonal bracing? "X" bracing?
                # In alternate cells
                
                # Cell coordinates
                cell_x = int(angle / sector)
                cell_y = int(z_mm / h_spacing)
                
                is_diag = False
                if (cell_x + cell_y) % 2 == 0:
                    # Draw X
                    # Map cell coords to 0..1
                    u = (angle % sector) / sector
                    v = (z_mm % h_spacing) / h_spacing
                    
                    # Diag 1: u = v
                    # Diag 2: u = 1-v
                    # Check distance to line u=v
                    
                    # dist = |Ax + By + C| / sqrt(A^2+B^2)
                    # u - v = 0 -> 1*u + (-1)*v + 0 = 0
                    # dist = |u-v| / sqrt(2)
                    
                    # Scale by cell size for mm width
                    # Approx cell width ~50mm
                    d1 = abs(u-v) * 50.0 / 1.414
                    d2 = abs(u-(1.0-v)) * 50.0 / 1.414
                    
                    if d1 < (beam_thick/2.0) or d2 < (beam_thick/2.0):
                        is_diag = True
                
                if is_vert or is_horz or is_diag:
                    # Solid beam
                    # Must be within shell thickness bounds?
                    # Yes, already checked above.
                    
                    # Additional check: Hand access
                    if dist_xy > hand_access_radius:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "architect_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
