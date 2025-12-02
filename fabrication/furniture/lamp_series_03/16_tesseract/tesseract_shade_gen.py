import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE TESSERACT (SHADE)
# -----------------------------------------------------------------------------
# Logic: 4D Hypercube Projection (Wireframe).
# Method: Define 16 vertices of 4D cube, project to 3D, create thick edges.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE TESSERACT SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Tesseract Logic
    # 16 Vertices in 4D: (+/-1, +/-1, +/-1, +/-1)
    # Project to 3D: (x,y,z,w) -> (x,y,z) * (1 / (w_dist - w)) perspective?
    # Or simple orthographic with rotation.
    
    vertices_4d = []
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                for w in [-1, 1]:
                    vertices_4d.append(np.array([x, y, z, w]))
    
    # Edges (32 edges)
    edges_4d = []
    for i in range(16):
        for j in range(i+1, 16):
            dist = np.linalg.norm(vertices_4d[i] - vertices_4d[j])
            if abs(dist - 2.0) < 0.1: # Connected if dist is 2 (change 1 coordinate)
                edges_4d.append((i, j))
                
    # Rotations in 4D (XY, XZ, XW, YZ, YW, ZW)
    # Let's rotate XW and ZW to unfold it slightly
    angle_xw = math.pi / 4.0
    angle_zw = math.pi / 4.0
    
    def rotate_4d(v):
        # XW
        x, y, z, w = v
        nx = x * math.cos(angle_xw) - w * math.sin(angle_xw)
        nw = x * math.sin(angle_xw) + w * math.cos(angle_xw)
        x, w = nx, nw
        # ZW
        nz = z * math.cos(angle_zw) - w * math.sin(angle_zw)
        nw = z * math.sin(angle_zw) + w * math.cos(angle_zw)
        z, w = nz, nw
        return np.array([x, y, z, w])
    
    # Project to 3D
    # Stereographic projection: v3 = v4_xyz / (2 - w)
    projected_verts = []
    scale_factor = diameter * 0.35 # Scale to fit shade
    
    for v in vertices_4d:
        vr = rotate_4d(v)
        x, y, z, w = vr
        denom = 2.5 - w
        p = np.array([x, y, z]) / denom
        projected_verts.append(p * scale_factor)
        
    # Shift Z to center in shade height
    z_offset = height / 2.0
    for i in range(16):
        projected_verts[i][2] += z_offset
        
    # Build SDF from Edges
    # Dist to line segment
    def dist_to_segment(p, v1, v2):
        ab = v2 - v1
        ap = p - v1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0.0, min(1.0, t))
        closest = v1 + t * ab
        return np.linalg.norm(p - closest)
        
    edge_radius = 6.0 # Thick wireframe
    
    radius = diameter / 2.0
    
    print("Constructing Hypercube...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                p_curr = np.array([x_mm, y_mm, z_mm])
                
                # --- PRIORITY 1: SPIDER FITTER ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > (radius-15.0): # Solid Ring
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: WIREFRAME ---
                # Find min dist to any edge
                min_dist = 999.0
                
                # Optimization: Bounding box check?
                # Just brute force 32 edges is fine for resolution 100^3
                
                for e in edges_4d:
                    v1 = projected_verts[e[0]]
                    v2 = projected_verts[e[1]]
                    d = dist_to_segment(p_curr, v1, v2)
                    if d < min_dist:
                        min_dist = d
                
                if min_dist < edge_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "tesseract_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
