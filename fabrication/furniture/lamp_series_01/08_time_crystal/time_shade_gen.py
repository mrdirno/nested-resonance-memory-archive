import numpy as np
import math
import sys
import struct
import random

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE TIME CRYSTAL (SHADE)
# -----------------------------------------------------------------------------
# Logic: 
# 1. Concept: Repeating Structure in Time (Rotational Symmetry breaking).
# 2. Math: Twisted Voronoi / Low Poly Faceting with periodic rotation.
# 3. Standard: 1-Inch Wall, SOLID TOP CAP, Hand Access.
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

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=12.5):
    print(f"Generating TIME CRYSTAL SHADE: {output_path}")
    
    # Mount Parameters (Standard V7/V8 Solid Cap)
    mount_hole_radius = hole_diameter / 2.0 
    bottom_rim_height = 2.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Crystal Generation
    # Faceted Shell
    # Define a set of cutting planes that rotate with Z
    
    num_faces = 8
    twist_total = math.pi / 2.0 # 90 deg twist
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    print("Crystallizing Time...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Twist angle at this height
        theta_z = z_norm * twist_total
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # --- PRIORITY 1: SOLID TOP CAP (MOUNTING) ---
                if z_mm > (height - 4.0):
                    if dist_from_center_xy < mount_hole_radius:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        if dist_from_center_xy < radius:
                             grid[x_idx,y_idx,z_idx] = True
                    continue

                # --- PRIORITY 2: CRYSTAL SHELL ---
                is_solid = False
                
                if dist_from_center_xy < hand_access_radius:
                    is_solid = False
                else:
                    # Define Crystal shape
                    # Rotate point by -theta_z to bring it to base frame
                    rx = x_mm * math.cos(-theta_z) - y_mm * math.sin(-theta_z)
                    ry = x_mm * math.sin(-theta_z) + y_mm * math.cos(-theta_z)
                    
                    # Polygon check (Octagon)
                    # Max(abs(dot(p, normal_i)))
                    # Octagon normals: (1,0), (0.7,0.7), (0,1), ...
                    # Simplify: Max of projected distance on axes
                    
                    # Just use polar coord mod?
                    angle = math.atan2(ry, rx)
                    # Quantize angle
                    sector = 2*math.pi / num_faces
                    a_quant = math.floor(angle / sector) * sector + (sector/2)
                    
                    # Distance to edge of polygon
                    # r * cos(angle - a_quant) = R_poly
                    # R_poly varies with Z (spherical envelope)
                    
                    # Sphere radius at this Z
                    # R_s = sqrt(R^2 - (z - z_c)^2)
                    if dist_spherical <= radius and dist_spherical > (radius - wall_thickness):
                        # It's in the sphere shell.
                        # Now apply Facet Mask
                        # We want the surface to be faceted.
                        # So effective radius is modulated.
                        
                        mod = math.cos(angle - a_quant)
                        # If we want flat faces, R must increase at corners?
                        # R_trace = R_flat / cos(diff)
                        
                        # Let's just subtract volume
                        # If dist_xy > (R_sphere * mod)? No
                        
                        # Simple Facet Logic:
                        # Union of planes?
                        # Let's stick to the Sphere Shell but apply a "Crystal Texture"
                        # Voronoi surface texture
                        
                        # Or simple:
                        # Only keep if near the center of a face?
                        # Let's use the Twist to define the wall.
                        
                        # Modulation
                        m = math.cos(num_faces/2 * angle) # 4 lobes
                        
                        # Add "Time Crystal" Texture (Periodic Geometric Noise)
                        # Use high freq sine waves aligned with the facets
                        texture_scale = 2.0 * math.pi / 15.0 # 15mm detail
                        tex = math.sin(rx * texture_scale) * math.sin(ry * texture_scale) * math.sin(z_mm * texture_scale)
                        
                        # Apply texture to radius threshold
                        # Effective radius slightly modulated by texture
                        # This creates a "glitchy" crystalline surface
                        
                        # Base polygon bound already defined by twist? 
                        # We need to actually CUT the volume.
                        # Let's use Voronoi-like intersection logic simplified
                        
                        # If distance to center < radius AND inside polygon AND texture condition
                        # Polygon logic:
                        # d_poly = dist_from_center_xy * math.cos(angle - a_quant)
                        # Boundary: d_poly < R_eff
                        
                        # R_eff varies with Z (sphere)
                        # R_sphere_at_z = math.sqrt(radius**2 - (effective_z - sphere_z_center)**2)
                        # Let's say the crystal is inscribed in the sphere.
                        
                        if dist_spherical < radius:
                             # Texture check: Only keep 80% of the volume near surface?
                             # Or simply emboss?
                             # Let's emboss:
                             if tex > 0.5:
                                 # Additive bump? No, boolean logic.
                                 is_solid = True
                             else:
                                 # Main body
                                 # Keep solid if deep enough
                                 if dist_spherical < (radius - 2.0):
                                     is_solid = True

                # --- PRIORITY 3: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         is_solid = True
                         
                grid[x_idx,y_idx,z_idx] = is_solid

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_y):
                y_mm = (y * step) - (diameter/2)
                if not grid[x,y,z]: continue
                s2 = step/2
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/08_time_crystal/time_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
