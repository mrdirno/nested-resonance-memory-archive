import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V49 (Catalog #114): THE BLANCMANGE CURVE (Takagi Extrusion)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the Takagi (Blancmange) curve.
#          This is a pathological function that is continuous everywhere but
#          differentiable nowhere, constructed by summing triangle waves.
# Parents: 117_weierstrass (Fractal Function), 57_dini (Surface).
# Math: Sum_{n=0}^{inf} (1/2^n) * s(2^n * x), where s(x) is triangle wave.
# -----------------------------------------------------------------------------

def takagi_function(x, iterations=10):
    # Calculate Takagi curve value at x (0 to 1)
    val = 0.0
    for n in range(iterations):
        # Frequency 2^n
        # Amplitude 1/2^n
        freq = 2.0**n
        amp = 1.0 / (2.0**n)
        
        # Triangle wave of period 1: abs(x - round(x)) ?
        # Triangle wave s(x) = dist(x, nearest integer)
        
        tx = x * freq
        s = abs(tx - round(tx)) # Distance to nearest integer
        
        val += amp * s
        
    return val

def generate_child_v49(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V49 (The Blancmange Curve): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 25.0
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # ---------------------------------------------------------
    # BLANCMANGE LATTICE
    # ---------------------------------------------------------
    
    # We map the Takagi function to the cylinder radius.
    # r(theta) = R_base + A * Takagi(theta)
    # Or we create a lattice based on the function surface.
    
    # Let's create a surface of revolution where the profile is the Takagi curve?
    # No, that's just a bumpy vase.
    
    # Let's wrap the Takagi curve around the cylinder as a "Wave".
    # r(theta, z) = R + Takagi(theta) * scale
    # But we want a lattice.
    
    # How about:
    # The lamp is defined by `z = Takagi(r) + Takagi(theta)`?
    # Or intersection of `y > Takagi(x)` style logic?
    
    # Let's do: The surface is a "Pudding" (Blancmange) shape.
    # The wall thickness is modulated by the fractal.
    # And we punch holes where the curvature is high? Or just a lattice.
    
    # Let's map the Takagi curve to the Z-height of a spiral.
    # A spiral ramp where the height oscillates fractally.
    
    # Function:
    # H(theta) = z + Takagi(theta) * scale
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Twist
        twist = z_mm * 0.02
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # 1. MOUNTING
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                cap_check = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap_check is not None:
                    grid[x_idx,y_idx,z_idx] = cap_check
                    continue
                
                spider_check = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider_check is not None:
                    grid[x_idx,y_idx,z_idx] = spider_check
                    continue
                
                # 2. SHELL
                if z_mm < 4.0:
                    hand_radius = radius - shell_thickness
                    if dist_xy < radius and dist_xy > hand_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    # 3. BLANCMANGE PATTERN
                    
                    # Map theta
                    theta = math.atan2(y_mm, x_mm)
                    u = (theta + math.pi) / (2.0 * math.pi)
                    
                    # Add twist to u
                    u = (u + z_mm * 0.005) % 1.0
                    
                    # Takagi value (fractal height)
                    t_val = takagi_function(u, iterations=6)
                    # Range 0 to approx 0.66
                    
                    # Modulate radius or thickness?
                    # Let's create "Ridges".
                    # If z matches the Takagi landscape.
                    
                    # Map z to 0-1 over a segment height?
                    # Repeated bands.
                    
                    segment_h = 20.0
                    z_local = (z_mm % segment_h) / segment_h
                    
                    # Intersection
                    # z_local approx t_val ?
                    
                    # Band thickness
                    # Thicker bands
                    band_t = 0.25
                    
                    # Shift t_val to center
                    t_val_norm = t_val / 0.7
                    
                    # Fractal Wave
                    if abs(z_local - t_val_norm) < band_t:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        # Secondary reinforcement
                        # Gyroid
                        base_scale = 2.0 * math.pi / 15.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Thicker lattice
                        if abs(g_val) < 0.45:
                            grid[x_idx,y_idx,z_idx] = True
                        
                        # Vertical Ribs
                        # 12 ribs around
                        elif (u * 12.0) % 1.0 < 0.1:
                            grid[x_idx,y_idx,z_idx] = True
                        else:
                            grid[x_idx,y_idx,z_idx] = False
                        
                else:
                     grid[x_idx,y_idx,z_idx] = False

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_114_blancmange_curve.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v49(output_file)
