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

def generate_lamp_base_v4(output_path, 
                          diam=180.0,       
                          height=25.0,      
                          resolution=150):
    
    print(f"Generating Helios Lamp Base V4 (Manifold QA): {output_path}")
    
    # Uniform Grid
    res_x = resolution
    res_y = resolution
    step = diam / resolution
    res_z = int(height / step)
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: {step:.2f}mm)")
    
    radius = diam / 2.0
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # QA
    channel_width = 8.0
    channel_height = 8.0
    foot_radius = 10.0
    foot_offset = radius - 20.0
    foot_depth = 3.0
    hole_radius = 7.0
    solid_core_radius = 20.0
    
    scale = 2.0 * math.pi / 30.0
    
    print("Calculating Field (Manifold Logic)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step
        
        for x_idx in range(res_x):
            px = (x_idx * step) - radius
            for y_idx in range(res_y):
                py = (y_idx * step) - radius
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Boundary
                if r > radius: continue
                
                # 2. Subtractions
                # Nut Recess (Counterbore for mounting hardware)
                if r < 15.0 and pz < 6.0:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if r < hole_radius: 
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                if (px > 0) and (abs(py) < channel_width/2) and (pz < channel_height):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                is_foot = False
                if pz < foot_depth:
                    if math.sqrt((px-foot_offset)**2 + py**2) < foot_radius: is_foot = True
                    elif math.sqrt((px+foot_offset)**2 + py**2) < foot_radius: is_foot = True
                    elif math.sqrt(px**2 + (py-foot_offset)**2) < foot_radius: is_foot = True
                    elif math.sqrt(px**2 + (py+foot_offset)**2) < foot_radius: is_foot = True
                if is_foot:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 3. Additions
                if r < solid_core_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                if (pz < 2.0) or (pz > height - 2.0) or (r > radius - 2.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 4. Gyroid
                val = math.sin(px * scale) * math.cos(py * scale) + \
                      math.sin(py * scale) * math.cos(pz * scale) + \
                      math.sin(pz * scale) * math.cos(px * scale)
                      
                if abs(val) < 0.4:
                    grid[x_idx,y_idx,z_idx] = True

    # Meshing
    vertices = []
    faces = []
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))
        
    s = step / 2.0
    
    print("Meshing...")
    for z in range(res_z):
        pz = z * step
        for x in range(res_x):
            px = (x * step) - radius
            for y in range(res_y):
                if not grid[x,y,z]: continue
                
                py = (y * step) - radius
                
                if x==res_x-1 or not grid[x+1,y,z]:
                    add_quad((px+s,py-s,pz-s), (px+s,py+s,pz-s), (px+s,py+s,pz+s), (px+s,py-s,pz+s))
                if x==0 or not grid[x-1,y,z]:
                    add_quad((px-s,py-s,pz+s), (px-s,py+s,pz+s), (px-s,py+s,pz-s), (px-s,py-s,pz-s))
                if y==res_y-1 or not grid[x,y+1,z]:
                    add_quad((px+s,py+s,pz-s), (px-s,py+s,pz-s), (px-s,py+s,pz+s), (px+s,py+s,pz+s))
                if y==0 or not grid[x,y-1,z]:
                    add_quad((px-s,py-s,pz-s), (px+s,py-s,pz-s), (px+s,py-s,pz+s), (px-s,py-s,pz+s))
                if z==res_z-1 or not grid[x,y,z+1]:
                    add_quad((px+s,py-s,pz+s), (px+s,py+s,pz+s), (px-s,py+s,pz+s), (px-s,py-s,pz+s))
                if z==0 or not grid[x,y,z-1]:
                    add_quad((px-s,py-s,pz-s), (px-s,py+s,pz-s), (px+s,py+s,pz-s), (px+s,py-s,pz-s))

    write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        generate_lamp_base_v4("test_base_v4.stl")
    else:
        generate_lamp_base_v4(sys.argv[1])