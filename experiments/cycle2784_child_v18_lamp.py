import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V18: THE NAUTILUS SHELL (Logarithmic Spiral)
# -----------------------------------------------------------------------------
# Concept: A shell structure that follows the Golden Ratio (Phi) in a 3D spiral.
#          Chambers are defined by a modulated Gyroid lattice that grows
#          exponentially as it wraps around.
# Parents: 18_nautilus_shell (2D Spiral), 29_fibonacci_spiral (Math).
# Math: r = a * e^(b * theta)
# -----------------------------------------------------------------------------

def generate_child_v18(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V18 (The Nautilus Shell): {output_path}")

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
    
    # Nautilus Parameters
    # Logarithmic Spiral: r = a * exp(b * theta)
    # Growth factor b = ln(Phi) / (pi/2) approx 0.306 for golden spiral
    b = 0.17 # Tuned for lamp proportions
    a = 5.0
    
    # We want a 3D spiral: Helix + Expansion
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
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
                    # 3. NAUTILUS SPIRAL
                    # We define a "Spiral Coordinate"
                    # The spiral wall is where r approx a * exp(b * theta)
                    
                    # Map angle to [0, 2pi] plus rotations
                    # We want continuous spiral, so use unwrapped angle?
                    # Hard in explicit grid.
                    
                    # Instead, use implicit form: r - a * exp(b * (theta + 2*pi*n)) = 0
                    
                    # Better: Use a scrolling modulation of a Gyroid
                    # Modulate scale with radius?
                    
                    # Let's create spiral ridges using a sine wave of log(r) - theta
                    # phase = log(r/a)/b - theta
                    
                    # Avoid log(0)
                    r_safe = max(0.1, dist_xy)
                    
                    # Spiral Phase
                    # twist Z into it for 3D
                    phase = (math.log(r_safe/a) / b) - angle + (z_mm * 0.05)
                    
                    # Evaluate sine of phase -> Spiral Walls
                    spiral_val = math.cos(phase)
                    
                    # Combine with Gyroid for structure between spiral walls
                    # Rotate coords to align with spiral
                    
                    base_scale = 2.0 * math.pi / 18.0
                    
                    # Local lattice
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                    
                    # Composite:
                    # Spiral walls (high density) + Gyroid infill (medium density)
                    # We want the spiral to "carve" the gyroid or "reinforce" it?
                    # Let's reinforce: The spiral walls are solid ridges.
                    
                    # Spiral Wall Threshold
                    # Thickened for robustness
                    is_spiral_wall = spiral_val > 0.6
                    
                    # Gyroid Infill
                    # Thickened for connectivity
                    is_gyroid = abs(g_val) < 0.45
                    
                    if is_spiral_wall or is_gyroid:
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
    output_file = os.path.join(output_dir, "child_v18_nautilus_shell.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v18(output_file)
