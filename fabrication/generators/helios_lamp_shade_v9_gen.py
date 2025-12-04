import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE QUANTUM FOAM (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic:
# 1. Concept: Bubbling Space-Time.
# 2. Math: Schwarz P Surface (Primitive).
# 3. Standard: 1-Inch Wall, SPIDER FITTER (Hub + Spokes), Hand Access.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating QUANTUM FOAM SHADE (SCHWARZ P): {output_path}")

    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0
    hub_radius = 20.0 # 40mm Hub
    spoke_width = 8.0
    top_plate_height = 4.0
    bottom_rim_height = 4.0

    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = (diameter / 2.0) - wall_thickness # Exact 1 inch rim

    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution

    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1

    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")

    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)

    # Schwarz P Parameters
    base_scale = 2.0 * math.pi / 40.0

    print("Calculating Foam Field...")

    radius = diameter / 2.0
    sphere_z_center = height - radius

    for z_idx in range(res_z):
        z_mm = z_idx * step

        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)

            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)

                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)

                # Effective Z for Connection Guarantee
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0

                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)

                # Calculate current shell outer radius at this Z for Dynamic Constraint
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                if term < 0: term = 0
                current_shell_radius = math.sqrt(term)

                # --- PRIORITY 1: ROBUST SOLID CAP (User Mandate) ---
                # Force a solid 4mm thick washer at the top
                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_from_center_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=current_shell_radius # Full width cap
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue

                # --- PRIORITY 1.5: SPIDER FITTER (Hub + Spokes) ---
                # Connects the central Hub to the Outer Shell in the top region
                spider_z_start = height - 40.0
                if z_mm > spider_z_start:
                    # 1. Central Hub
                    if dist_from_center_xy < hub_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    # 2. Spokes (3-Way Symmetry)
                    # Distance to lines passing through origin at 0, 60, 120 degrees (relative to Y axis?)
                    # V6 Logic:
                    # d1: Distance to X-axis (y=0) -> Angle 0/180
                    # d2, d3: +/- 60 degrees from X-axis
                    
                    spoke_half = spoke_width / 2.0
                    
                    # Line 1: Y = 0 (Distance is abs(y))
                    d1 = abs(y_mm)
                    
                    # Line 2: Y = sqrt(3)*X
                    # General line Ax + By + C = 0 distance is |Ax0 + By0 + C| / sqrt(A^2+B^2)
                    # sqrt(3)X - Y = 0 -> A=sqrt(3), B=-1. Norm=2.
                    d2 = abs(math.sqrt(3)*x_mm - y_mm) / 2.0
                    
                    # Line 3: Y = -sqrt(3)*X
                    # sqrt(3)X + Y = 0 -> A=sqrt(3), B=1. Norm=2.
                    d3 = abs(math.sqrt(3)*x_mm + y_mm) / 2.0
                    
                    if d1 < spoke_half or d2 < spoke_half or d3 < spoke_half:
                         # Ensure we don't generate spokes outside the shell radius (optional, but cleaner)
                         if dist_from_center_xy < radius: 
                            grid[x_idx,y_idx,z_idx] = True
                            continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue
                
                # --- PRIORITY 3: SHELL & FOAM PATTERN ---
                is_solid = False
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                
                # Hand Access Void: Only apply below the Spider Fitter
                in_hand_void = (dist_from_center_xy < hand_access_radius) and (z_mm <= spider_z_start)
                
                is_void = in_inner_void or in_hand_void

                if in_outer_shell and not is_void:
                    # INNER SKIN (Connectivity Anchor)
                    # Force 3mm solid skin to prevent floating islands
                    if dist_spherical < (radius - wall_thickness + 3.0):
                        is_solid = True
                    else:
                        # Schwarz P Surface
                        lx = x_mm * base_scale
                        ly = y_mm * base_scale
                        lz = z_mm * base_scale

                        val = math.cos(lx) + math.cos(ly) + math.cos(lz)

                        if abs(val) < 0.60: # Thickened walls for robustness (0.35 -> 0.60)
                            is_solid = True

                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "quantum_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
