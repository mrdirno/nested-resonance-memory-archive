import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE LATTICE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Crystal Lattice (Bravais).
# Method: Atom (Sphere) and Bond (Cylinder) construction.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE LATTICE SHADE: {output_path}")
    
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
    
    # Lattice Logic
    # FCC or BCC structure.
    # Simple cubic for clarity?
    # Let's do a rotated cubic lattice (Diamond structure)
    
    # Atom positions
    # Grid spacing
    l_space = 30.0 
    atom_r = 6.0
    bond_r = 2.5
    
    print("Building Crystal Structure...")
    
    radius = diameter / 2.0
    
    # Helper: Distance to segment
    def dist_to_segment(p, v1, v2):
        ab = v2 - v1
        ap = p - v1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0.0, min(1.0, t))
        closest = v1 + t * ab
        return np.linalg.norm(p - closest)
        
    # Generate lattice points within the shell volume
    # Only generate near the shell to save computation
    # Shell bounds: radius to radius-thickness
    
    # We need a list of atoms and bonds
    atoms = []
    bonds = []
    
    # Rotated grid basis
    # 45 deg rotation
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    basis = np.array([[inv_sqrt2, -inv_sqrt2, 0],
                      [inv_sqrt2, inv_sqrt2, 0],
                      [0, 0, 1]])
    
    # Scan range
    rng = int(radius / l_space) + 2
    z_rng = int(height / l_space) + 2
    
    for ix in range(-rng, rng):
        for iy in range(-rng, rng):
            for iz in range(0, z_rng):
                # Lattice point
                pt = np.array([ix*l_space, iy*l_space, iz*l_space])
                
                # Rotate
                # pt_rot = np.dot(basis, pt) # Simple rotation
                # Let's assume aligned for now, maybe rotate later
                
                pt_rot = pt 
                
                # Check if in shell
                r_pt = math.sqrt(pt_rot[0]**2 + pt_rot[1]**2)
                
                # Keep atoms near the shell wall
                if r_pt < (radius + l_space) and r_pt > (radius - wall_thickness - l_space):
                    atoms.append(pt_rot)
                    
                    # Add bonds to neighbors (positive direction to avoid dupes)
                    # +x
                    bonds.append((pt_rot, pt_rot + np.array([l_space, 0, 0])))
                    # +y
                    bonds.append((pt_rot, pt_rot + np.array([0, l_space, 0])))
                    # +z
                    bonds.append((pt_rot, pt_rot + np.array([0, 0, l_space])))
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                p_curr = np.array([x_mm, y_mm, z_mm])
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: LATTICE SHELL (Anisotropic) ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                is_solid = False
                
                # Anisotropy: Vertical Stretch (Z)
                sz = l_space * 1.5 # Cells are 1.5x taller
                
                gx = x_mm / l_space
                gy = y_mm / l_space
                gz = z_mm / sz # Stretched
                
                dx = abs(gx - round(gx)) * l_space
                dy = abs(gy - round(gy)) * l_space
                dz = abs(gz - round(gz)) * sz # Back to mm
                
                # Node (Ellipsoid)
                # Distance metric distorted by anisotropy
                dist_to_atom = math.sqrt(dx*dx + dy*dy + (dz/1.5)**2) # Normalize Z for distance
                
                if dist_to_atom < atom_r:
                    is_solid = True
                else:
                    # Bonds
                    # Bond along Z (Vertical)
                    if math.sqrt(dx*dx + dy*dy) < bond_r: is_solid = True
                    # Bond along X (Horizontal)
                    elif math.sqrt(dy*dy + (dz/1.5)**2) < bond_r: is_solid = True
                    # Bond along Y (Horizontal)
                    elif math.sqrt(dx*dx + (dz/1.5)**2) < bond_r: is_solid = True
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lattice_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
