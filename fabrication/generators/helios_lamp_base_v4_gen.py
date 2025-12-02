import numpy as np
import math
import sys
import struct

def write_binary_stl(filename, vertices, faces):
    """
    Writes a mesh to a Binary STL file.
    """
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
                          diam=180.0,       # Diameter
                          height=25.0,      # Height (increased slightly for channel clearance)
                          resolution=100):
    
    print(f"Generating Helios Lamp Base V4 (QA Compliant): {output_path}")
    
    radius = diam / 2.0
    
    # Channel Config
    channel_width = 8.0 
    channel_height = 8.0
    
    # Feet Config
    foot_radius = 10.0
    foot_offset = radius - 20.0
    foot_depth = 3.0
    
    # Center Hole
    hole_radius = 7.0 # 14mm diam
    solid_core_radius = 20.0
    
    # Grid
    res_x = resolution
    res_y = resolution
    step_ref = diam / resolution
    res_z = int(height / step_ref)
    
    step_x = diam / res_x
    step_y = diam / res_y
    step_z = height / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_x:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Gyroid Params
    scale = 2.0 * math.pi / (30.0) # 30mm wavelength
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        
        for x_idx in range(res_x):
            px = (x_idx * step_x) - radius
            
            for y_idx in range(res_y):
                py = (y_idx * step_y) - radius
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. GLOBAL BOUNDARY (Cylinder)
                if r > radius:
                    continue
                
                # 2. SUBTRACTIONS (Negative Space)
                
                # A. Center Hole
                if r < hole_radius:
                    grid[x_idx, y_idx, z_idx] = False
                    continue
                    
                # B. Wire Channel (Tunnel)
                # Running along +X axis from center
                if (px > 0) and (abs(py) < channel_width/2) and (pz < channel_height):
                     grid[x_idx, y_idx, z_idx] = False
                     continue
                     
                # C. Feet Recesses
                # 4 feet at 90 degrees
                # Positions: (offset,0), (-offset,0), (0,offset), (0,-offset)
                is_foot = False
                if pz < foot_depth:
                    if math.sqrt((px-foot_offset)**2 + py**2) < foot_radius: is_foot = True
                    elif math.sqrt((px+foot_offset)**2 + py**2) < foot_radius: is_foot = True
                    elif math.sqrt(px**2 + (py-foot_offset)**2) < foot_radius: is_foot = True
                    elif math.sqrt(px**2 + (py+foot_offset)**2) < foot_radius: is_foot = True
                
                if is_foot:
                    grid[x_idx, y_idx, z_idx] = False
                    continue

                # 3. ADDITIONS (Solid Space)
                
                # A. Solid Core (around hole)
                if r < solid_core_radius:
                    grid[x_idx, y_idx, z_idx] = True
                    continue
                    
                # B. Solid Rim (Top and Bottom, and Outer Edge)
                if (pz < 2.0) or (pz > height - 2.0) or (r > radius - 2.0):
                    grid[x_idx, y_idx, z_idx] = True
                    continue
                
                # 4. GYROID FILL
                val = math.sin(px * scale) * math.cos(py * scale) + \
                      math.sin(py * scale) * math.cos(pz * scale) + \
                      math.sin(pz * scale) * math.cos(px * scale)
                      
                if abs(val) < 0.4:
                    grid[x_idx, y_idx, z_idx] = True

    print("Meshing...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        pz = z_idx * step_z
        
        for x_idx in range(res_x):
            px = (x_idx * step_x) - radius
            
            for y_idx in range(res_y):
                py = (y_idx * step_y) - radius
                
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                vx = px
                vy = py
                vz = pz
                
                s2x = step_x / 2
                s2y = step_y / 2
                s2z = step_z / 2
                
                # Neighbor Checks
                if x_idx == res_x-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                if y_idx == res_y-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_binary_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default test
        generate_lamp_base_v4("test_base_v4.stl")
    else:
        output_file = sys.argv[1]
        generate_lamp_base_v4(output_file)
