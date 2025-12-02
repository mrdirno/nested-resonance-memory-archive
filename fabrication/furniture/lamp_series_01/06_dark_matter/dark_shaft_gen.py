import numpy as np
import math
import sys
import struct
import random

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE DARK MATTER (SHAFT)
# -----------------------------------------------------------------------------
# Logic:
# 1. Shape: Filamentary Void (Bundle of Twisted Strands).
# 2. Core: 14mm Central Channel.
# 3. Ends: 10mm Holes.
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

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating DARK MATTER SHAFT: {output_path}")
    
    # Dimensions
    base_radius = 25.0
    
    # Core
    core_radius = 7.0 
    nipple_radius = 5.0 
    nipple_depth = 15.0 
    
    step = height / resolution
    
    res_x = int(2 * base_radius / step) + 2
    res_y = int(2 * base_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Strands Setup
    num_strands = 8
    strand_radius = 6.0
    twist_rate = 1.5 * 2 * math.pi # 1.5 turns over height
    
    # Precompute strand centers? No, z varies.
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Rotation at this height
        angle_offset = z_norm * twist_rate
        
        # Radius of bundle might vary? Narrow waist?
        bundle_radius = 15.0
        if z_norm > 0.3 and z_norm < 0.7:
            bundle_radius = 12.0 # Slight waist
        
        strand_centers = []
        for i in range(num_strands):
            theta = (i / num_strands) * 2 * math.pi + angle_offset
            sx = bundle_radius * math.cos(theta)
            sy = bundle_radius * math.sin(theta)
            strand_centers.append((sx, sy))
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - base_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - base_radius
                
                dist_sq = x_mm**2 + y_mm**2
                dist = math.sqrt(dist_sq)
                
                is_solid = False
                
                # Check strands
                for sc in strand_centers:
                    sx, sy = sc
                    d_strand = math.sqrt((x_mm-sx)**2 + (y_mm-sy)**2)
                    if d_strand < strand_radius:
                        is_solid = True
                        break
                
                # Ensure center is solid for core channel?
                # Or add central pillar?
                # Let's add a central pillar that merges
                if dist < (core_radius + 3.0):
                    is_solid = True

                # Inner Core
                if dist < core_radius:
                    is_solid = False
                    
                # Nipple Holes
                if z_mm < nipple_depth or z_mm > (height - nipple_depth):
                    # Force solid cap for hardware
                    if dist < 12.0: is_solid = True
                    if dist < nipple_radius: is_solid = False
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - base_radius
            for y in range(res_y):
                y_mm = (y * step) - base_radius
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
    output_file = "fabrication/furniture/lamp_series_01/06_dark_matter/dark_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
