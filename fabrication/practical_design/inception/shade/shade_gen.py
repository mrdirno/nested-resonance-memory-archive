import numpy as np
import math
import sys
import struct
import os

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (PRISM MATH RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2836:
# - Goal: Restore the "Original" Anisotropic Prism math which features "Coordinate Scaling".
# - Effect: "Big Bang" (Small waves top, Large waves bottom) emerges naturally from taper scaling.
# - Source: fabrication/generators/helios_anisotropic_prism_gen.py (Commit 88fb2c2c).
# - Geometry: V2.4 (217.65mm H, 85.4mm Top, 194mm Base).
# - Features: Hollow Shell (Variable Wall), Breathable (No Inner Skin), No Twist.
# -----------------------------------------------------------------------------

def write_binary_stl(filename, vertices, faces):
    # Inline binary STL writer from original generator
    def normal(v1, v2, v3):
        u = v2 - v1
        w = v3 - v1
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        n = np.array([nx, ny, nz])
        nm = np.linalg.norm(n)
        return n / nm if nm > 0 else np.array([0, 0, 1])

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

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC PRISM SHADE v2.4: {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")

    # Wall Thickness (Variable)
    wall_bottom = 12.7 # 1/2 inch
    wall_top = 6.35    # 1/4 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # MATH PARAMETERS (From helios_anisotropic_prism_gen.py)
    # Base pattern scale was: 2.0 * pi / (base_size / 3.0)
    # 194 / 3.0 = 64.6mm Wavelength (Large Waves)
    base_pattern_scale = 2.0 * math.pi / (base_width / 3.0)
    
    # Z Scale
    # Original used size_z / 3.0
    # 217 / 3.0 = 72.5mm Z-Wavelength
    base_scale_z = 2.0 * math.pi / (height / 3.0)
    
    # K Expansion (Taper)
    # scale = 1 + k * z_norm
    # top = base * (1 + k) -> k = (top/base) - 1
    k_expansion = (top_width / base_width) - 1.0
    print(f"K Expansion: {k_expansion:.4f}")
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # 1. Taper Logic (Coordinate Scaling)
        # This matches the "Prism" generator logic exactly
        shape_scale_factor = 1.0 + k_expansion * z_norm
        if shape_scale_factor < 0.01: shape_scale_factor = 0.01
        
        # Physical Dimensions at this Z
        current_width = base_width * shape_scale_factor
        
        # Variable Wall Logic (Added for Shade)
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        for x_idx in range(res_xy):
            px_unscaled = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                py_unscaled = (y_idx * step) - (base_width / 2.0)
                
                # 2. BOUNDARY CHECKS (Physical)
                # Check against PHYSICAL dimensions (unscaled for outer, scaled for wall)
                # Wait, px_unscaled is the grid coordinate centered at 0.
                # Outer limit is current_outer_half_width.
                
                if abs(px_unscaled) > current_outer_half_width or abs(py_unscaled) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(px_unscaled**2 + py_unscaled**2)
                
                # --- MOUNTING LOGIC ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(px_unscaled) < current_outer_half_width and abs(py_unscaled) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                if z_mm < 4.0:
                    if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # --- HOLLOW SHELL LOGIC ---
                if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 3. PATTERN MATH (Coordinate Scaling)
                # px = px_unscaled * (base / current) 
                # This keeps the NUMBER of waves constant, shrinking them as the shade tapers.
                # Result: Small waves at Top, Large at Bottom.
                
                ratio = base_width / current_width
                px = px_unscaled * ratio
                py = py_unscaled * ratio
                
                # Standard Gyroid
                # No Twist, No Z-Warp (Standard Z scale)
                
                val = math.sin(px * base_pattern_scale) * math.cos(py * base_pattern_scale) + \
                      math.sin(py * base_pattern_scale) * math.cos(z_mm * base_scale_z) + \
                      math.sin(z_mm * base_scale_z) * math.cos(px * base_pattern_scale)
                      
                if abs(val) < 0.5: # Standard Iso
                    grid[x_idx,y_idx,z_idx] = True

    # Extract Isosurface (Voxel Meshing from Original)
    print("Extracting Isosurface (Voxel)...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            for y_idx in range(res_xy):
                if not grid[x_idx,y_idx,z_idx]: continue
                
                # Voxel Center
                vx = (x_idx * step) - (base_width / 2.0)
                vy = (y_idx * step) - (base_width / 2.0)
                vz = z_idx * step
                
                s = step / 2.0
                
                # 6 Neighbors
                if x_idx == res_xy-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s, vy-s, vz-s), (vx+s, vy+s, vz-s), (vx+s, vy+s, vz+s), (vx+s, vy-s, vz+s))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s, vy-s, vz+s), (vx-s, vy+s, vz+s), (vx-s, vy+s, vz-s), (vx-s, vy-s, vz-s))
                if y_idx == res_xy-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s, vy+s, vz-s), (vx-s, vy+s, vz-s), (vx-s, vy+s, vz+s), (vx+s, vy+s, vz+s))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s, vy-s, vz-s), (vx+s, vy-s, vz-s), (vx+s, vy-s, vz+s), (vx-s, vy-s, vz+s))
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s, vy-s, vz+s), (vx+s, vy+s, vz+s), (vx-s, vy+s, vz+s), (vx-s, vy-s, vz+s))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s, vy-s, vz-s), (vx-s, vy+s, vz-s), (vx+s, vy+s, vz-s), (vx+s, vy-s, vz-s))

    write_binary_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
