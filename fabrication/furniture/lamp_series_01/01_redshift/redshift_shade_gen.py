import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (SHADE)
# -----------------------------------------------------------------------------
# Logic: Anisotropic Gyroid Frustum + Solid Top Ring (40mm hole) + Solid Bottom Rim
# -----------------------------------------------------------------------------

def write_binary_stl(filename, vertices, faces):
    def normal(v1, v2, v3):
        u = v2 - v1
        w = v3 - v1
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        n = np.array([nx, ny, nz])
        norm = np.linalg.norm(n)
        return n / norm if norm > 0 else np.array([0, 0, 1])

    num_triangles = len(faces)
    print(f"Writing Binary STL ({num_triangles} triangles)...")

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', num_triangles))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            data = struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2])
            f.write(data)
            f.write(struct.pack('<H', 0))

def generate_shade(output_path, base_width=180.0, top_width=80.0, height=150.0, resolution=150, hole_diameter=42.0):
    print(f"Generating REDSHIFT SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0
    solid_rim_height = 4.0 # mm (Bottom and Top solid thickness)
    wall_thickness = 25.4 # 1 inch
    
    # Hub Parameters (Inner Ring)
    hub_thickness = 5.0
    hub_radius_inner = mount_hole_radius
    hub_radius_outer = mount_hole_radius + hub_thickness
    
    # Spoke Parameters
    spoke_width = 6.0
    
    # Grid Setup
    # Max dimension determines voxel size
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_x = int(base_width / step) + 5 # Padding
    res_y = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Frequency Setup (Gyroid)
    base_scale = 2.0 * math.pi / (base_width / 4.0) # 4 periods across base
    
    # Z-Modulation (Redshift)
    # Wavelength increases with Z (Frequency decreases)
    k_mod = 0.5 # Strong redshift
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Normalized Z (0 to 1)
        z_norm = z_mm / height
        
        # Frustum Width at current Z
        # Linear interpolation: Width = Base * (1 - z) + Top * z
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_outer_radius = current_width / 2.0
        current_inner_radius = current_outer_radius - wall_thickness
        
        # Safety Check for Mounting
        # If we are at the top, ensure we have enough width for the hole
        if z_mm > (height - solid_rim_height):
            if current_outer_radius < mount_hole_radius + 2.0:
                print(f"WARNING: Top width ({current_width:.1f}mm) is too narrow for hole ({hole_diameter}mm) at Z={z_mm:.1f}!")
        
        # Scale factor for conformal mapping
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        # Z-Scale (Redshift)
        current_scale_z = base_scale / (1.0 + k_mod * z_norm)
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Bounding Box Check (Outer Frustum Shape)
                if dist_from_center_xy > current_outer_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- PRIORITY 1: TOP MOUNT (SPIDER FITTER) ---
                # Hub + Spokes for heat dissipation
                if z_mm > (height - solid_rim_height):
                    # Hub (Washer Seat / Inner Ring)
                    hub_radius_inner = mount_hole_radius
                    hub_radius_outer = mount_hole_radius + 8.0 # 16mm thick ring (robust)
                    
                    # Spokes (Rods)
                    spoke_width = 8.0 # Thicker rods
                    
                    # Check Hub (Inner Ring)
                    if dist_from_center_xy < hub_radius_inner:
                        grid[x_idx,y_idx,z_idx] = False # Hole
                        continue
                    
                    if dist_from_center_xy < hub_radius_outer:
                        grid[x_idx,y_idx,z_idx] = True # Solid Hub
                        continue
                        
                    # Check Spokes (Rods connecting Hub to Wall)
                    if dist_from_center_xy < current_inner_radius:
                        in_spoke_x = abs(x_mm) < (spoke_width/2)
                        in_spoke_y = abs(y_mm) < (spoke_width/2)
                        
                        if in_spoke_x or in_spoke_y:
                            grid[x_idx,y_idx,z_idx] = True
                        else:
                            grid[x_idx,y_idx,z_idx] = False # Air Gap
                        continue

                # Solid base rim for bed adhesion and stability
                if z_mm < solid_rim_height:
                     # Check hollow core for bottom? Usually bottom is just the wall ring.
                     # Or should it be a solid floor?
                     # User asked for "hollow". So let's respect the wall thickness even at bottom.
                     if dist_from_center_xy < current_inner_radius:
                         grid[x_idx,y_idx,z_idx] = False
                         continue
                     else:
                         grid[x_idx,y_idx,z_idx] = True # Solid Wall Ring
                     continue

                # --- PRIORITY 3: BODY (HOLLOW + GYROID) ---
                
                # Hollow Core Check
                if dist_from_center_xy < current_inner_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Gyroid Infill (Within the wall)
                lx = x_mm * scale_factor
                ly = y_mm * scale_factor
                lz = z_mm 
                
                val = math.sin(lx * base_scale) * math.cos(ly * base_scale) + \
                      math.sin(ly * base_scale) * math.cos(lz * current_scale_z) + \
                      math.sin(lz * current_scale_z) * math.cos(lx * base_scale)
                
                if abs(val) < 0.4: # Wall thickness
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False


    print("Extracting Mesh...")
    
    # Standard Marching Cubes / Voxel extraction (Simplified Quad)
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - (base_width/2)
            for y in range(res_y):
                y_mm = (y * step) - (base_width/2)
                
                if not grid[x,y,z]: continue
                
                # Center
                v_c = (x_mm, y_mm, z_mm)
                s2 = step/2
                
                # Check neighbors
                if x==res_x-1 or not grid[x+1,y,z]:
                    add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]:
                    add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]:
                    add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]:
                    add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==res_z-1 or not grid[x,y,z+1]:
                    add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]:
                    add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    # Default to current directory if running from within the folder, or explicit path
    output_file = "redshift_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    
    generate_shade(output_file)
