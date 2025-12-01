import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE)
# -----------------------------------------------------------------------------
# Logic: Schwarz D (Diamond) Dome + Solid Top Ring + Solid Bottom Rim
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

def generate_shade(output_path, diameter=160.0, height=140.0, resolution=100, hole_diameter=42.0):
    print(f"Generating EVENT HORIZON SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0
    solid_rim_height = 4.0 
    wall_thickness = 15.0 # Thickness of the TPMS shell roughly
    
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
    
    # Frequency Setup (Schwarz D)
    # Adjust for aesthetic density
    scale = 2.0 * math.pi / (diameter / 5.0) # 5 periods across diameter
    
    print("Calculating Field (Schwarz D)...")
    
    radius = diameter / 2.0
    
    # Sphere Center (assuming dome sits on z=0)
    # To make a dome of height H from a sphere of radius R, we need to offset Z.
    # If H < 2R, we are cutting a sphere.
    # Let's center the sphere at z = height - radius.
    # So top of sphere is at z = height.
    sphere_z_center = height - radius
    # If height=140, radius=80 -> center at z=60. Top at 140. Bottom at -20 (clipped at 0).
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                # Spherical Boundary
                dist_sq = x_mm**2 + y_mm**2 + (z_mm - sphere_z_center)**2
                
                if dist_sq > radius**2:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)

                # --- PRIORITY 1: TOP PLATE (MOUNTING) ---
                if z_mm > (height - solid_rim_height):
                    if dist_from_center_xy < mount_hole_radius:
                        grid[x_idx,y_idx,z_idx] = False # Hole
                    else:
                        grid[x_idx,y_idx,z_idx] = True # Solid Plate
                    continue 
                
                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < solid_rim_height:
                    # Solid ring at bottom
                    inner_r = radius - wall_thickness # Rough inner
                    if dist_sq < (radius-5)**2: # Hollow out bottom rim?
                         # Let's make it a ring
                         if dist_from_center_xy < (radius - 10): # 10mm thick ring
                             grid[x_idx,y_idx,z_idx] = False
                         else:
                             grid[x_idx,y_idx,z_idx] = True
                    else:
                         grid[x_idx,y_idx,z_idx] = True
                    continue

                # --- PRIORITY 3: BODY (SCHWARZ D) ---
                
                # Hollow Core Check (Optional - Schwarz D is usually volumetric, but we want a shell)
                # Let's mask out the very center if we want a hollow lamp.
                # Actually, TPMS can be the shell itself.
                # We want the surface where Equation = 0 (with thickness).
                
                lx = x_mm * scale
                ly = y_mm * scale
                lz = z_mm * scale
                
                # Schwarz D approximation
                # sin(x)sin(y)sin(z) + sin(x)cos(y)cos(z) + cos(x)sin(y)cos(z) + cos(x)cos(y)sin(z) = 0
                
                sx, sy, sz = math.sin(lx), math.sin(ly), math.sin(lz)
                cx, cy, cz = math.cos(lx), math.cos(ly), math.cos(lz)
                
                val = sx*sy*sz + sx*cy*cz + cx*sy*cz + cx*cy*sz
                
                # Thickness threshold
                # Range of val is roughly [-1.5, 1.5] (not exact)
                # We want a shell around val=0
                if abs(val) < 0.3: 
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False


    print("Extracting Mesh (Voxel Quad)...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_y):
                y_mm = (y * step) - (diameter/2)
                
                if not grid[x,y,z]: continue
                
                # Neighbor checks
                s2 = step/2
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
    output_file = "fabrication/furniture/lamp_series_01/02_event_horizon/event_horizon_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    
    generate_shade(output_file)
