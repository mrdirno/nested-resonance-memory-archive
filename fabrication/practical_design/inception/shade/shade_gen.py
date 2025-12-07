import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic:
# 1. 1-Inch Thick Wall (Robustness).
# 2. 200mm Diameter (Max Print Area).
# 3. Connection Guarantee: Flattened Top Shell to ensure Spokes connect to something.
# 4. Refined Hub: 40mm Diameter (Spider Fitter).
# 5. Refined Bottom Rim: 4mm Thick.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=150, hole_diameter=14.0):
    print(f"Generating EVENT HORIZON SHADE (V7 CONNECTION FIX): {output_path}")

    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0
    hub_radius = 20.0 # 40mm Dia
    spoke_width = 8.0
    top_plate_height = 4.0

    # Bottom Rim (Refined)
    bottom_rim_height = 4.0

    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = 45.0

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

    # Frequency Setup
    target_period = 48.5
    start_scale = 2.0 * math.pi / 60.0
    end_scale = 2.0 * math.pi / target_period

    print("Calculating Field...")

    radius = diameter / 2.0
    sphere_z_center = height - radius

    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height

        # Scale
        current_scale = start_scale * (1.0 - z_norm) + end_scale * z_norm

        # Calculate outer shell radius at this Z for fitter constraint
        effective_z = z_mm
        if z_mm > (height - 10.0):
            effective_z = height - 10.0

        dz = effective_z - sphere_z_center

        # Safe sqrt
        term = radius**2 - dz**2
        if term < 0: term = 0
        current_shell_radius = math.sqrt(term)

        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)

            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)

                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)

                # Calculate Spherical Distance
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)

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

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: ACCRETION VEIL PATTERN ---
                is_solid = False
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                in_hand_void = dist_from_center_xy < hand_access_radius
                is_void = in_inner_void or in_hand_void

                if in_outer_shell and not is_void:
                    # ACCRETION VEIL (Robust Connectivity)

                    # Vortex Domain Warp
                    # Instead of rotating coordinates, warp them
                    # Twist around Z

                    angle = math.atan2(y_mm, x_mm)
                    r = dist_from_center_xy

                    # Twist increases with Z and R
                    twist = (z_mm/height * 2.0 * math.pi) + (r/radius * 2.0 * math.pi)

                    # Warped Angle
                    angle_warped = angle + twist

                    # Map back to Cartesian for Gyroid
                    tx = r * math.cos(angle_warped)
                    ty = r * math.sin(angle_warped)

                    scale = 2.0 * math.pi / 40.0 # Lower freq (was 30.0)

                    # Gyroid
                    val = math.sin(tx*scale)*math.cos(ty*scale) + \
                          math.sin(ty*scale)*math.cos(z_mm*scale) + \
                          math.sin(z_mm*scale)*math.cos(tx*scale)

                    is_lattice = abs(val) < 0.85 # Thicker (was 0.80)

                    # STRUCTURAL RIBS (Spokes - Thickened)
                    rib_val = math.sin(4.0 * angle_warped)
                    is_rib = rib_val > 0.6 # Very thick ribs (was 0.85)

                    if is_lattice or is_rib:
                        is_solid = True

                    # INNER SKIN (Connectivity Guarantee)
                    # Force solid at the inner boundary to bind loose ends
                    # Inner radius is (radius - wall_thickness)
                    # We want to fill from inner_radius to inner_radius + 4.0
                    r_inner = radius - wall_thickness
                    if dist_from_center_xy > r_inner and dist_from_center_xy < (r_inner + 4.0):
                        is_solid = True

                    if is_solid:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False

                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction (Library)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "event_horizon_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
