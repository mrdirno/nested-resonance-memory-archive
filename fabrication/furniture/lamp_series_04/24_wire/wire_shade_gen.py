import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 04: THE WIRE (SHADE)
# -----------------------------------------------------------------------------
# Logic: Vector Graphic / Low Poly.
# Method: Wireframe Mesh (Edges of a low-poly geometry).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE WIRE SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
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
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Wireframe Logic
    # We need to define a low-poly mesh (vertices and edges)
    # Then render the edges as thick cylinders.
    
    # Geometry: Icosahedron or Geodesic Dome approximation
    # Let's do a triangulated cylinder.
    
    # Vertices
    verts = []
    edges = []
    
    radius = diameter / 2.0
    num_rings = 6
    num_segments = 12
    
    # Generate Vertices
    for i in range(num_rings + 1):
        z = (i / num_rings) * height
        
        # Twist or taper?
        # Slight taper
        r_ring = radius * (1.0 - 0.2 * (z/height))
        
        # Offset alternate rings for triangulation
        offset = 0.0
        if i % 2 == 1: offset = (math.pi / num_segments)
        
        for j in range(num_segments):
            theta = (j / num_segments) * 2 * math.pi + offset
            x = r_ring * math.cos(theta)
            y = r_ring * math.sin(theta)
            verts.append(np.array([x, y, z]))
            
    # Generate Edges
    # Horizontal
    for i in range(num_rings + 1):
        start_idx = i * num_segments
        for j in range(num_segments):
            idx1 = start_idx + j
            idx2 = start_idx + ((j + 1) % num_segments)
            edges.append((verts[idx1], verts[idx2]))
            
    # Vertical / Diagonal
    for i in range(num_rings):
        start_curr = i * num_segments
        start_next = (i + 1) * num_segments
        
        for j in range(num_segments):
            # Connect to nearest neighbors
            # If offset, indices align differently
            
            # Just connect all reasonable neighbors
            # Simplest triangulation:
            # current j connects to next j and next j-1 (if offset)
            # Or simply nearest distance.
            
            v_curr = verts[start_curr + j]
            
            # Find 2 closest in next ring
            closest = []
            for k in range(num_segments):
                v_next = verts[start_next + k]
                dist = np.linalg.norm(v_curr - v_next)
                closest.append((dist, start_next + k))
            
            closest.sort(key=lambda x: x[0])
            
            # Add edges to 2 nearest
            edges.append((v_curr, verts[closest[0][1]]))
            edges.append((v_curr, verts[closest[1][1]]))
            
    print(f"Rendering {len(edges)} vectors...")
    
    # Helper
    def dist_to_segment(p, v1, v2):
        ab = v2 - v1
        ap = p - v1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0.0, min(1.0, t))
        closest = v1 + t * ab
        return np.linalg.norm(p - closest)
    
    wire_radius = 3.0
    
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
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: WIREFRAME SHELL ---
                
                if dist_xy > (radius + 10.0): # Bounds check
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Check Edges
                min_dist = 999.0
                
                # Optimization needed? 
                # Filter edges by Z height
                for e in edges:
                    v1, v2 = e
                    # Z bounds of edge
                    min_z = min(v1[2], v2[2]) - wire_radius
                    max_z = max(v1[2], v2[2]) + wire_radius
                    
                    if z_mm >= min_z and z_mm <= max_z:
                        d = dist_to_segment(p_curr, v1, v2)
                        if d < min_dist: min_dist = d
                        
                if min_dist < wire_radius:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "wire_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
