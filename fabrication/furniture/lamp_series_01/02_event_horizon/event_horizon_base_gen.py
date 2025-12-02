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

def generate_base(output_path, diameter=140.0, height=30.0, resolution=60):
    print(f"Generating EVENT HORIZON BASE (V2 FIX): {output_path}")
    
    # Dimensions
    radius = diameter / 2.0
    shaft_radius = 7.6 # 15.2mm Diameter
    rod_radius = 5.2 
    wire_channel_width = 6.0
    wire_channel_height = 6.0
    wall_thickness = 2.4
    
    # Feet Parameters
    foot_offset = 10.0
    foot_radius = 10.0
    foot_depth = 2.0
    
    # Nut Trap
    nut_height = 8.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (diameter/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (diameter/2)
                
                dist_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- LOGIC STACK ---
                is_solid = False
                
                # 1. Base Cylinder
                if dist_center <= radius:
                    is_solid = True
                
                # 2. Hollow Ballast
                if wall_thickness < z_mm < (height - wall_thickness):
                    if dist_center < (radius - wall_thickness) and dist_center > (shaft_radius + wall_thickness):
                         is_solid = False

                # 3. Center Hole
                if dist_center < rod_radius:
                    is_solid = False
                    
                # 4. Shaft Socket (Top)
                if z_mm > (height - 10.0): 
                    if dist_center < shaft_radius:
                        is_solid = False

                # 5. Wire Channel
                # Ensure it cuts through the rim
                if z_mm < wire_channel_height and \
                   abs(x_mm) < (wire_channel_width/2) and \
                   y_mm > 0:
                    is_solid = False

                # 6. Feet Recesses (Bottom Corners)
                if z_mm < foot_depth:
                    # 4 points around center
                    # We are in a cylinder, so let's place 4 feet at 45, 135, 225, 315 degrees
                    # Radius of foot centers = radius - foot_offset - foot_radius/2
                    r_feet = radius - foot_offset - foot_radius/2
                    
                    # Check distance to any of 4 feet
                    # Foot 1 (North East)
                    d1 = math.sqrt((x_mm - r_feet*0.707)**2 + (y_mm - r_feet*0.707)**2)
                    # Foot 2 (North West)
                    d2 = math.sqrt((x_mm + r_feet*0.707)**2 + (y_mm - r_feet*0.707)**2)
                    # Foot 3 (South West)
                    d3 = math.sqrt((x_mm + r_feet*0.707)**2 + (y_mm + r_feet*0.707)**2)
                    # Foot 4 (South East)
                    d4 = math.sqrt((x_mm - r_feet*0.707)**2 + (y_mm + r_feet*0.707)**2)
                    
                    if min(d1, d2, d3, d4) < foot_radius:
                         is_solid = False

                # 7. Nut Trap
                if z_mm < nut_height:
                    if dist_center < 10.0: 
                        is_solid = False

                grid[x_idx,y_idx,z_idx] = is_solid

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_xy):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_xy):
                y_mm = (y * step) - (diameter/2)
                if not grid[x,y,z]: continue
                
                s2 = step/2
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/02_event_horizon/event_horizon_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)