import numpy as np
import math
import sys
import struct
import random

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE MULTIVERSE (SHADE)
# -----------------------------------------------------------------------------
# Logic: 
# 1. Concept: Bubble Universes (Sphere Packing).
# 2. Math: Boolean Union of random spheres on a shell.
# 3. Standard: 1-Inch Wall, Spider Fitter V7 (SOLID RIM), Hand Access.
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

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=12.5):
    print(f"Generating MULTIVERSE SHADE (BUBBLE PACKING): {output_path}")
    
    # Mount Parameters (Standard V7)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 13.0 
    spoke_width = 6.0 
    top_plate_height = 5.0 
    bottom_rim_height = 2.0 
    
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
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Bubble Packing
    # We want spheres centered *on* the shell wall, of varying sizes.
    # If a point is inside ANY sphere, it's solid.
    # But we also need to respect the void/shell boundaries?
    # No, the bubbles *form* the shell.
    
    bubbles = []
    random.seed(1234)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # Distribute bubbles on the surface of the master sphere
    num_bubbles = 500
    
    for _ in range(num_bubbles):
        # Random point on sphere surface
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        
        # Radius varies: shell radius +/- some variance
        r_center = radius * random.uniform(0.9, 1.0)
        
        bx = r_center * math.sin(phi) * math.cos(theta)
        by = r_center * math.sin(phi) * math.sin(theta)
        bz = r_center * math.cos(phi) + sphere_z_center
        
        # Bubble size ( Reduced for Scale Constraint )
        b_rad = random.uniform(6.0, 18.0)
        
        bubbles.append((bx, by, bz, b_rad))
    
    print("Inflating Universes...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0
                
                # --- PRIORITY 1: SOLID TOP CAP (MOUNTING) ---
                if z_mm > (height - 4.0):
                    # Central Hole (12.5mm dia)
                    if dist_from_center_xy < (12.5 / 2.0):
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        # Solid Cap connecting to shell
                        if dist_from_center_xy < radius:
                             grid[x_idx,y_idx,z_idx] = True
                    continue

                # --- PRIORITY 2: BUBBLE SHELL ---
                is_solid = False
                
                # Hand access void overrides everything in the center
                if dist_from_center_xy < hand_access_radius:
                    is_solid = False
                else:
                    # FORCE SOLID RIM at Top
                    if z_mm > (height - top_plate_height):
                        # Ensure we are within outer radius
                        if dist_from_center_xy < radius:
                            is_solid = True
                    else:
                        # Check bubbles
                        # Optimization: Check distance to shell center first?
                        dist_to_center = math.sqrt(x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2)
                        if dist_to_center > (radius + 25.0) or dist_to_center < (radius - 50.0):
                            is_solid = False # Optimization
                        else:
                            for b in bubbles:
                                bx, by, bz, br = b
                                d = (x_mm-bx)**2 + (y_mm-by)**2 + (z_mm-bz)**2
                                if d < (br**2):
                                    is_solid = True
                                    break
                        
                # --- PRIORITY 3: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         is_solid = True
                         
                grid[x_idx,y_idx,z_idx] = is_solid

    print("Extracting Mesh...")
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
                s2 = step/2
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/07_multiverse/multiverse_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
