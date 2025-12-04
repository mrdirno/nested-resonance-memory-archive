import numpy as np
import math
import sys
import os
from scipy.special import sph_harm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# -----------------------------------------------------------------------------
# CHILD V20: THE ATOMIC ORBITAL (Quantum Probability)
# -----------------------------------------------------------------------------
# Concept: A visualization of the probabilistic location of an electron.
#          Combines s-orbitals (spheres) and d-orbitals (lobes/donuts).
#          A "Cloud" of matter that is dense where probability is high.
# Parents: 20_atomic_orbital (Concept), 06_quantum_foam (Physics).
# Math: |Psi|^2 > Threshold. Psi = R(r) * Y_lm(theta, phi).
# -----------------------------------------------------------------------------

def radial_wavefunction(r, n=3, l=2):
    # Simplified Hydrogen-like radial function
    # R_nl(r) approx r^l * exp(-r/n) * LaguerrePoly(r)
    # We just use the shape characteristic: peak at Bohr radius
    
    # Normalize r to "Bohr Radii" scale
    # Tuned for connection
    rho = r * 0.18
    
    # Simple approximation for visual shape
    # Peak at r = n^2
    # Decay e^-r/n
    
    val = (rho**l) * math.exp(-rho/2.0)
    return val

def generate_child_v20(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V20 (The Atomic Orbital): {output_path}")

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
    
    # Orbital Parameters (3d_z2 orbital - donut shape)
    n = 3
    l = 2
    m = 0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Orbital Twist? Electrons have spin...
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
                    # 3. ORBITAL LATTICE
                    
                    # Spherical Coords
                    if dist_spherical == 0:
                        theta = 0
                        phi = 0
                    else:
                        z_norm = max(-1.0, min(1.0, dz / dist_spherical))
                        theta = math.acos(z_norm)
                        phi = math.atan2(y_mm, x_mm)
                    
                    # Twist Phi (Spin)
                    phi_twisted = phi + twist
                    
                    # Wavefunction
                    # Radial part
                    R = radial_wavefunction(dist_spherical, n, l)
                    
                    # Angular part (Spherical Harmonic)
                    Y = sph_harm(m, l, phi_twisted, theta)
                    
                    # Probability Density
                    prob = (abs(Y * R))**2
                    
                    # We need a lattice structure, not just a cloud.
                    # Intersection of Probability Cloud with a Gyroid?
                    # "Quantized" probability.
                    
                    # Gyroid backbone
                    base_scale = 2.0 * math.pi / 18.0
                    g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                            np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                            np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                            
                    # Modulate Gyroid thickness by Probability
                    
                    # Boosted density
                    density = prob * 800.0
                    
                    # Clamp density
                    density = min(1.0, density)
                    
                    # Lattice threshold
                    # Base scaffold (Quantum Foam) must be solid (0.5)
                    # Probability Cloud adds thickness
                    t_base = 0.5
                    t_cloud = 0.4 * density
                    
                    t = min(0.9, t_base + t_cloud)
                    
                    if abs(g_val) < t:
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
    output_file = os.path.join(output_dir, "child_v20_atomic_orbital.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v20(output_file)