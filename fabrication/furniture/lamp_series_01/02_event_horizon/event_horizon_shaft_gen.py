import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHAFT) - V3 HIGH COMPLEXITY
# -----------------------------------------------------------------------------
# Logic: 
# 1. Gravitational Lensing (Bulge).
# 2. Helical Twist (Event Horizon Spin).
# 3. Surface Interference Pattern (Accretion Texture).
# 4. Hollow Core (Cable Management).
# 5. Socket Recess (Top).
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

def generate_shaft(output_path, height=180.0, resolution=100):
    print(f"Generating EVENT HORIZON SHAFT (V3 COMPLEXITY): {output_path}")
    
    base_radius = 15.0 
    max_bulge = 12.0 # Significant gravitational distortion
    core_radius = 6.0 # 12mm ID (Cable)
    socket_recess_radius = 8.0 
    
    width = (base_radius + max_bulge + 5.0) * 2.0 # Padding for texture
    
    step = width / resolution
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Texture Frequencies
    twist_freq = 2.0 * math.pi / (height * 0.8) # ~1.2 full twists
    rib_freq = 12.0 # Number of vertical ribs
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # 1. Gravitational Lensing (Profile Radius)
        # Pinch at bottom, Bulge at middle, Taper at top
        # Sine wave modulated by linear taper
        bulge = max_bulge * math.sin(z_norm * math.pi)
        nominal_radius = base_radius + bulge
        
        # Twist Angle
        angle_offset = z_mm * twist_freq
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (width/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (width/2)
                
                dist_center = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # --- LOGIC STACK ---
                is_solid = False
                
                # 2. Complex Surface (Twisted Ribs)
                # Surface modulation
                # Cosine of (Angle + Twist) * Ribs
                texture = math.cos((angle + angle_offset) * rib_freq)
                
                # Texture Amplitude (Depth of ribs)
                # Ribs get deeper at the bulge (lensing effect magnification)
                rib_depth = 2.0 + (2.0 * math.sin(z_norm * math.pi))
                
                effective_radius = nominal_radius + (texture * rib_depth)
                
                if dist_center <= effective_radius:
                    is_solid = True
                    
                # 3. Hollow Core
                if dist_center < core_radius:
                    is_solid = False
                
                # 4. Socket Recess (Top)
                if z_mm > (height - 10.0):
                    if dist_center < socket_recess_radius:
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
            x_mm = (x * step) - (width/2)
            for y in range(res_xy):
                y_mm = (y * step) - (width/2)
                if not grid[x,y,z]: continue
                
                s2 = step/2
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/02_event_horizon/event_horizon_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
