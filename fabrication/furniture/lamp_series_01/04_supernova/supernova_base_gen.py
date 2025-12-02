import numpy as np
import math
import sys
import struct
import random

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SUPERNOVA (BASE)
# -----------------------------------------------------------------------------
# Logic:
# 1. Shape: Neutron Core (Faceted/Low-Poly).
# 2. Features: Wire Channel, Feet Recesses.
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

def generate_base(output_path, diameter=140.0, height=45.0, resolution=100):
    print(f"Generating SUPERNOVA BASE: {output_path}")
    
    radius = diameter / 2.0
    
    # Wire Channel
    channel_width = 8.0
    channel_height = 8.0
    
    # Feet
    feet_inset = 15.0
    feet_radius = 8.0
    feet_depth = 2.0
    
    # Central Hole
    center_hole_radius = 5.0 
    recess_radius = 20.0
    recess_depth = 5.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Generate Planes for Faceting
    # We want a low-poly approximate sphere/cylinder
    num_planes = 12
    planes = []
    random.seed(99)
    
    # Add a top plane to keep it flat-ish on top
    # No, top should be faceted too, but mount area flat?
    # Standard base usually needs flat mount area.
    # Let's define the solid as intersection of half-spaces.
    
    for i in range(num_planes):
        # Normal
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0.2, 1.5) # Mostly side/top angles
        nx = math.sin(phi) * math.cos(theta)
        ny = math.sin(phi) * math.sin(theta)
        nz = math.cos(phi)
        
        # Distance from center
        # We want a radius approx 'radius'
        d = radius * random.uniform(0.8, 1.1)
        planes.append((nx, ny, nz, d))
        
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                is_solid = True
                
                # Cylinder bound (optional, to keep footprint)
                if dist_xy > radius:
                    is_solid = False
                    
                # Height bound
                if z_mm > height:
                    is_solid = False
                
                if is_solid:
                    # Check planes (Cut away material)
                    # This creates a rock-like faceted shape
                    # Center (0,0, height/2)
                    
                    px = x_mm
                    py = y_mm
                    pz = z_mm - (height/2) 
                    
                    for p in planes:
                        nx, ny, nz, d = p
                        if (px*nx + py*ny + pz*nz) > d:
                            is_solid = False
                            break
                            
                # Wire Channel
                if z_mm < channel_height:
                    if x_mm > 0 and abs(y_mm) < (channel_width/2):
                        is_solid = False
                        
                # Feet
                if z_mm < feet_depth:
                    foot_dist = radius - feet_inset
                    if math.sqrt((x_mm-foot_dist)**2 + y_mm**2) < feet_radius: is_solid = False
                    if math.sqrt((x_mm+foot_dist)**2 + y_mm**2) < feet_radius: is_solid = False
                    if math.sqrt(x_mm**2 + (y_mm-foot_dist)**2) < feet_radius: is_solid = False
                    if math.sqrt(x_mm**2 + (y_mm+foot_dist)**2) < feet_radius: is_solid = False
                
                # Center Hole
                if dist_xy < center_hole_radius:
                    is_solid = False
                    
                # Hardware Recess
                if z_mm < recess_depth:
                    if dist_xy < recess_radius:
                        is_solid = False
                        
                # Top Flat Spot for Shaft Mount
                # Force flat area at top center
                if z_mm > (height - 2.0) and dist_xy < 20.0:
                     is_solid = True
                     # Re-check hole
                     if dist_xy < center_hole_radius: is_solid = False
                
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_xy):
            x_mm = (x * step) - radius
            for y in range(res_xy):
                y_mm = (y * step) - radius
                if not grid[x,y,z]: continue
                s2 = step/2
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/04_supernova/supernova_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
