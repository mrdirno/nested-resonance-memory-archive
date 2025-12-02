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

def generate_base(output_path, width=180.0, height=20.0, resolution=150):
    print(f"Generating BASE (The Void Series): {output_path}")
    
    # Dimensions
    rod_radius = 6.25 # 12.5mm Diameter
    wire_channel_width = 6.0
    wire_channel_height = 6.0
    
    # Gyroid Params
    base_scale = 2.0 * math.pi / 15.0 # 15mm wavelength
    
    step = width / resolution
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel: {step:.2f}mm)")
    
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
                
                # 1. Outer Bounds (Cylinder or Box? Reference says "Wide/Slim profile". Usually Round for lamps).
                # Let's assume Cylinder for "The Void" aesthetic (matches shaft).
                if dist_center > (width/2):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 2. Center Hole (Subtraction)
                if dist_center < rod_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 3. Wire Channel (Subtraction)
                if z_mm < wire_channel_height and \
                   abs(x_mm) < (wire_channel_width/2) and \
                   y_mm > 0:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 4. Solid Top/Bottom Skins (2mm)
                if z_mm < 2.0 or z_mm > (height - 2.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 5. Radial Gradient Gyroid
                # Center = Solid (High Threshold), Edge = Airy (Low Threshold)
                # Map dist from 0 to width/2
                
                # Solid Core Zone (around hole)
                if dist_center < 20.0:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Gradient Zone
                # Norm dist from 20 to 90
                d_norm = (dist_center - 20.0) / ((width/2) - 20.0)
                d_norm = max(0.0, min(1.0, d_norm))
                
                # Threshold: 0.8 (Solid) -> 0.15 (Airy)
                threshold = 0.8 - (d_norm * 0.65)
                
                val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                      math.sin(y_mm * base_scale) * math.cos(z_mm * base_scale) + \
                      math.sin(z_mm * base_scale) * math.cos(x_mm * base_scale)
                
                if abs(val) < threshold:
                    grid[x_idx,y_idx,z_idx] = True



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
    output_file = "redshift_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
