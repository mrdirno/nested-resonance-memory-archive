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

def generate_lamp_shade_v4(output_path, 
                           size_x=60.0,      # Top Size
                           size_y=60.0,      
                           size_z=220.0,     
                           resolution=150,   
                           k_mod=0.01,       
                           k_expansion=2.5,  
                           wall_thickness=25.4, 
                           hole_diam=14.0):
    
    print(f"Generating Helios Lamp Shade V4 (Manifold QA): {output_path}")
    
    # Dimensions
    max_width = size_x * (1.0 + k_expansion)
    
    # Uniform Grid
    res_x = resolution
    res_y = resolution
    step = max_width / resolution
    res_z = int(size_z / step)
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Parameters
    hub_diam = 40.0
    spoke_width = 8.0
    top_mount_height = 15.0
    
    base_scale_xy = 2.0 * math.pi / (size_x / 3.0)
    
    print("Calculating Field (Manifold Logic)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step
        z_norm = pz / size_z
        
        # Expansion Factor
        exp_factor = 1.0 + k_expansion * (1.0 - z_norm)
        current_width = size_x * exp_factor
        
        # Scale Modulation
        base_wavelength_z = size_z / 4.0
        scale_z = (2.0 * math.pi / base_wavelength_z) / (1 + k_mod * z_norm)
        
        dist_from_top = size_z - pz
        is_top_mount = (dist_from_top < top_mount_height)
        is_transition = (dist_from_top < top_mount_height + 10.0)
        
        for x_idx in range(res_x):
            px = (x_idx * step) - (max_width/2)
            
            for y_idx in range(res_y):
                py = (y_idx * step) - (max_width/2)
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Global Boundary
                if abs(px) > (current_width/2) or abs(py) > (current_width/2):
                    continue
                
                # 2. Spider Fitter (Triskelion)
                if is_top_mount:
                    if r < hole_diam/2: continue # Hole
                    if r < hub_diam/2: 
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    spoke_half = spoke_width/2
                    d1 = abs(py)
                    d2 = abs(-math.sqrt(3)*px - py)/2
                    d3 = abs(math.sqrt(3)*px - py)/2
                    if d1<spoke_half or d2<spoke_half or d3<spoke_half:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    dist_x = (current_width/2) - abs(px)
                    dist_y = (current_width/2) - abs(py)
                    if min(dist_x, dist_y) < wall_thickness:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    continue
                
                # 3. Wall Mask
                dist_x = (current_width/2) - abs(px)
                dist_y = (current_width/2) - abs(py)
                if min(dist_x, dist_y) > wall_thickness:
                    continue
                
                # 4. Solid Transition
                if is_transition:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 5. Pattern
                px_ref = px / exp_factor
                py_ref = py / exp_factor
                
                val = math.sin(px_ref * base_scale_xy) * math.cos(py_ref * base_scale_xy) + \
                      math.sin(py_ref * base_scale_xy) * math.cos(pz * scale_z) + \
                      math.sin(pz * scale_z) * math.cos(px_ref * base_scale_xy)
                      
                if abs(val) < 0.4:
                    grid[x_idx,y_idx,z_idx] = True

    # Meshing (Uniform Grid)
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
            px = (x * step) - (max_width/2)
            for y in range(res_y):
                if not grid[x,y,z]: continue
                
                py = (y * step) - (max_width/2)
                
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
        generate_lamp_shade_v4("test_shade_v4.stl")
    else:
        generate_lamp_shade_v4(sys.argv[1])