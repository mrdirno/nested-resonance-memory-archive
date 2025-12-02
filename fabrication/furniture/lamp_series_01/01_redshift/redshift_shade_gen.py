import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic: Anisotropic Gyroid Frustum (Square Pyramid)
# Dims: 194mm Base -> 60mm Top -> 224mm Height
# Mount: Spider Fitter (12.5mm Hole for Washer/Finial)
# Wall: 1 Inch Thick (Hollow)
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

def generate_shade(output_path, base_width=194.0, top_width=60.0, height=224.0, resolution=150, hole_diameter=12.5):
    print(f"Generating THE VOID SHADE: {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")
    
    # Mount Parameters (Washer Top / Finial Mount)
    mount_hole_radius = hole_diameter / 2.0
    hub_radius_outer = 15.0 # 30mm Diameter Hub (Solid Washer Seat)
    spoke_width = 6.0
    
    solid_rim_height = 4.0
    wall_thickness = 25.4 # 1 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Frequency
    base_scale = 2.0 * math.pi / (base_width / 4.0)
    k_mod = 0.5
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Square Frustum Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - wall_thickness
        
        # Scale factor
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        current_scale_z = base_scale / (1.0 + k_mod * z_norm)
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # 1. Bounding Box (Square Frustum)
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- PRIORITY 1: SOLID TOP CAP (MOUNTING) ---
                if z_mm > (height - 4.0):
                    # Central Hole (12.5mm dia)
                    if dist_from_center < (12.5 / 2.0):
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        # Solid Cap connecting to shell
                        if dist_from_center < current_outer_half_width:
                             grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 2: BOTTOM RIM (Solid Frame) ---
                if z_mm < solid_rim_height:
                    # Frame only (Hollow center)
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 3: REINFORCING CORNERS (Solid Edges) ---
                # Corners are at +/- width/2
                # If we are within 'edge_thickness' of BOTH x-edge and y-edge
                edge_thickness = 5.0
                
                in_x_edge = abs(x_mm) > (current_outer_half_width - edge_thickness)
                in_y_edge = abs(y_mm) > (current_outer_half_width - edge_thickness)
                
                if in_x_edge and in_y_edge:
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # --- PRIORITY 4: BODY (Gyroid in Walls) ---
                # Check Hollow Core
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Gyroid
                lx = x_mm * scale_factor
                ly = y_mm * scale_factor
                lz = z_mm
                
                val = math.sin(lx * base_scale) * math.cos(ly * base_scale) + \
                      math.sin(ly * base_scale) * math.cos(lz * current_scale_z) + \
                      math.sin(lz * current_scale_z) * math.cos(lx * base_scale)
                
                if abs(val) < 0.4:
                    grid[x_idx,y_idx,z_idx] = True
                else:
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
            x_mm = (x * step) - (base_width/2)
            for y in range(res_xy):
                y_mm = (y * step) - (base_width/2)
                
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
    output_file = "redshift_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)