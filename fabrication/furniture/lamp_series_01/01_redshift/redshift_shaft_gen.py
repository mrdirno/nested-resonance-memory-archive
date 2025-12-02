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

def generate_shaft(output_path, height=200.0, resolution=150):
    print(f"Generating ARTERIAL HELIX SHAFT: {output_path}")
    
    # Dimensions (The Void Series)
    base_diameter = 55.0
    top_diameter = 40.0
    core_id = 12.0 # 6mm radius hole
    core_od = 16.0 # 8mm radius solid wall
    
    # Helix Params
    helix_pitch = 150.0 # Elongated spiral
    helix_strands = 4
    
    # Grid
    max_width = base_diameter + 5.0
    step = max_width / resolution # XY resolution
    step_z = height / resolution  # Z resolution
    
    res_xy = int(max_width / step) + 5
    res_z = int(height / step_z) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Gyroid Params
    scale_base = 2.0 * math.pi / 15.0 # 15mm wavelength
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step_z
        z_norm = z_mm / height
        
        # Taper Logic
        current_diameter = base_diameter * (1.0 - z_norm) + top_diameter * z_norm
        current_radius = current_diameter / 2.0
        
        # Twist Angle for Helix
        angle = (z_mm / helix_pitch) * 2.0 * math.pi
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (max_width/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (max_width/2)
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Inner Hole (Void)
                if dist < (core_id / 2.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 2. Solid Core Wall (Artery)
                if dist < (core_od / 2.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 3. Outer Taper Limit
                if dist > current_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 4. Arterial Helix Logic (Variable Density Gyroid)
                # Calculate Polar Angle
                theta = math.atan2(y_mm, x_mm)
                
                # Helical Mask: sin(strands * theta + z_factor)
                # Creates spiral regions of positive/negative
                helix_val = math.sin(helix_strands * theta - (z_mm / helix_pitch * 2 * math.pi))
                
                # Gyroid Field
                gx, gy, gz = x_mm * scale_base, y_mm * scale_base, z_mm * scale_base
                gyroid_val = math.sin(gx)*math.cos(gy) + math.sin(gy)*math.cos(gz) + math.sin(gz)*math.cos(gx)
                
                # Variable Density Threshold
                # Center (near core) -> Solid (High threshold allows more)
                # Edge -> Airy (Low threshold allows less)
                # Map dist from [core_od/2] to [current_radius] -> [0, 1]
                d_norm = (dist - (core_od/2)) / (current_radius - (core_od/2))
                
                # Threshold: 0.8 (solid-ish) -> 0.2 (sparse)
                # If we want "Arterial", we want the HELIX to be solid-ish and the gaps to be empty?
                # Or we want the Helix to be the *structure*.
                
                # Let's try: Structure exists where Helix Mask > 0.
                # Inside that structure, we apply Gyroid.
                
                if helix_val > 0: # Inside a spiral arm
                    # Modulate gyroid thickness by radial distance
                    # Thicker at center, thinner at edge
                    thresh = 0.6 - (d_norm * 0.5) 
                    if abs(gyroid_val) < thresh:
                        grid[x_idx,y_idx,z_idx] = True

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Extraction loop (Standard)
    for z in range(res_z):
        z_mm = z * step_z
        for x in range(res_xy):
            x_mm = (x * step) - (max_width/2)
            for y in range(res_xy):
                y_mm = (y * step) - (max_width/2)
                if not grid[x,y,z]: continue
                
                s2 = step/2
                s2z = step_z/2
                
                # Note: step_z might be different from step (xy)
                # We need to adjust the quad generation to use s2z for Z coordinates
                
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2z), (x_mm+s2, y_mm+s2, z_mm-s2z), (x_mm+s2, y_mm+s2, z_mm+s2z), (x_mm+s2, y_mm-s2, z_mm+s2z))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2z), (x_mm-s2, y_mm+s2, z_mm+s2z), (x_mm-s2, y_mm+s2, z_mm-s2z), (x_mm-s2, y_mm-s2, z_mm-s2z))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2z), (x_mm-s2, y_mm+s2, z_mm-s2z), (x_mm-s2, y_mm+s2, z_mm+s2z), (x_mm+s2, y_mm+s2, z_mm+s2z))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2z), (x_mm+s2, y_mm-s2, z_mm-s2z), (x_mm+s2, y_mm-s2, z_mm+s2z), (x_mm-s2, y_mm-s2, z_mm+s2z))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2z), (x_mm+s2, y_mm+s2, z_mm+s2z), (x_mm-s2, y_mm+s2, z_mm+s2z), (x_mm-s2, y_mm-s2, z_mm+s2z))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2z), (x_mm-s2, y_mm+s2, z_mm-s2z), (x_mm+s2, y_mm+s2, z_mm-s2z), (x_mm+s2, y_mm-s2, z_mm-s2z))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/redshift_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
