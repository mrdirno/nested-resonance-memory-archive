import numpy as np
import math
import sys
import struct

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

def generate_base(output_path, width=120.0, height=30.0, resolution=60):
    print(f"Generating BASE BLOCK (Protocol V1.0): {output_path}")
    
    # Dimensions
    shaft_radius = 7.6 # 15.2mm Diameter (Socket)
    rod_radius = 5.2 # 10.4mm Diameter (Through Hole)
    wire_channel_width = 6.0
    wire_channel_height = 6.0
    wall_thickness = 2.4 # 6 perimeters
    
    # Feet
    foot_offset = 10.0 # from edge
    foot_radius = 10.0 # 20mm diameter recess
    foot_depth = 2.0
    
    # Nut Trap (M10)
    nut_width = 17.0 # Flat to Flat (Standard M10 is 17mm, add tolerance)
    nut_height = 8.0
    
    step = width / resolution
    
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (width/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (width/2)
                
                dist_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Base Block (Union)
                if abs(x_mm) < (width/2) and abs(y_mm) < (width/2):
                    grid[x_idx,y_idx,z_idx] = True
                
                # 2. Hollow Ballast Chamber (Subtraction)
                # Leave walls and floor/ceiling
                if wall_thickness < z_mm < (height - wall_thickness):
                    if abs(x_mm) < (width/2 - wall_thickness) and abs(y_mm) < (width/2 - wall_thickness):
                        # Don't hollow out the central column (for the rod)
                        if dist_center > (shaft_radius + wall_thickness):
                             grid[x_idx,y_idx,z_idx] = False
                
                # 3. Center Hole (Through Rod)
                if dist_center < rod_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    
                # 4. Shaft Socket (Top only)
                if z_mm > (height - 10.0): # 10mm deep socket
                    if dist_center < shaft_radius:
                        grid[x_idx,y_idx,z_idx] = False

                # 5. Wire Channel (Bottom)
                if z_mm < wire_channel_height and \
                   abs(x_mm) < (wire_channel_width/2) and \
                   y_mm > 0:
                    grid[x_idx,y_idx,z_idx] = False
                    
                # 6. Feet Recesses (Bottom Corners)
                if z_mm < foot_depth:
                    # 4 corners
                    fx = width/2 - foot_offset - foot_radius/2
                    fy = width/2 - foot_offset - foot_radius/2
                    
                    # Check dist to any of 4 feet centers
                    if math.sqrt((abs(x_mm)-fx)**2 + (abs(y_mm)-fy)**2) < foot_radius:
                         grid[x_idx,y_idx,z_idx] = False
                         
                # 7. Nut Trap (Bottom Center)
                # Simple Hex approximation (Circle for now, or Box?)
                # M10 Hex is ~19.6mm corner-to-corner. Let's use 20mm cylinder for simplicity/compatibility
                if z_mm < nut_height:
                    if dist_center < (20.0 / 2):
                        grid[x_idx,y_idx,z_idx] = False


    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_xy):
            x_mm = (x * step) - (width/2)
            for y in range(res_xy):
                y_mm = (y * step) - (width/2)
                if not grid[x,y,z]: continue
                
                s2 = step/2
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/redshift_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
