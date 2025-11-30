import json
import numpy as np
import sys
import math

def write_stl(filename, vertices, faces):
    """
    Writes a mesh to an ASCII STL file.
    vertices: List or array of (x, y, z) coordinates.
    faces: List of (v1_idx, v2_idx, v3_idx) tuples.
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

    with open(filename, 'w') as f:
        f.write(f"solid {filename}\n")
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            
            f.write(f"facet normal {n[0]:.4f} {n[1]:.4f} {n[2]:.4f}\n")
            f.write("  outer loop\n")
            f.write(f"    vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}\n")
            f.write(f"    vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}\n")
            f.write(f"    vertex {v3[0]:.4f} {v3[1]:.4f} {v3[2]:.4f}\n")
            f.write("  endloop\n")
            f.write("endfacet\n")
        f.write(f"endsolid {filename}\n")

def generate_pc_token(json_path, output_path):
    # 1. Load Data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    pc_id = data.get("pc_id", "UNKNOWN")
    mean_pop = data["discovery"]["features"]["mean_population"]
    std_pop = data["discovery"]["features"]["std_population"]
    
    print(f"Generating Token for {pc_id}")
    print(f"Mean Pop: {mean_pop}, Std Dev: {std_pop}")

    # 2. Geometry Parameters
    radius = 20.0  # mm
    base_height = 3.0
    max_feature_height = 5.0
    segments = 60
    
    vertices = []
    faces = []
    
    # Helper to add vertex
    def add_vert(x, y, z):
        vertices.append((x, y, z))
        return len(vertices) - 1

    # 3. Generate Base Cylinder (Bottom Cap + Walls)
    center_bottom = add_vert(0, 0, 0)
    
    # Rim vertices (Bottom and Top-Base)
    bottom_rim = []
    base_top_rim = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        bottom_rim.append(add_vert(x, y, 0))
        base_top_rim.append(add_vert(x, y, base_height))
        
    # Bottom Cap Faces
    for i in range(segments):
        v1 = center_bottom
        v2 = bottom_rim[i]
        v3 = bottom_rim[(i + 1) % segments]
        # Clockwise for bottom looking down, so counter-clockwise looking up?
        # STL normal rule: Right hand rule. Vertices CCW -> Normal Out.
        # Bottom face normal points down (0,0,-1).
        faces.append((v1, v3, v2)) 
        
    # Wall Faces
    for i in range(segments):
        b1 = bottom_rim[i]
        b2 = bottom_rim[(i + 1) % segments]
        t1 = base_top_rim[i]
        t2 = base_top_rim[(i + 1) % segments]
        
        faces.append((b1, b2, t1))
        faces.append((b2, t2, t1))

    # 4. Generate Data Landscape (Top Surface)
    # We create a grid of points inside the circle
    grid_res = 20
    grid_verts = {} # map (r_idx, theta_idx) -> v_idx
    
    # We will use polar coordinates for the grid to match the rim
    center_top_idx = add_vert(0, 0, base_height + (mean_pop / 100.0)) # Central peak? No, keep it flat-ish
    
    # Re-generate top surface using concentric rings
    rings = 10
    prev_ring_indices = [center_top_idx] * segments # Start with center point treated as a ring of 0 radius
    
    for r in range(1, rings + 1):
        current_ring_radius = (radius / rings) * r
        current_ring_indices = []
        
        for s in range(segments):
            angle = 2 * math.pi * s / segments
            
            # DATA MAPPING:
            # The Z height is modulated by the PC statistics.
            # Pattern: A radial wave + noise
            # Frequency increases with radius
            
            # Normalized distance from center (0 to 1)
            dist_norm = r / rings
            
            # Wave function
            wave = math.sin(angle * 6) * math.cos(dist_norm * 10)
            
            # Modulation
            z_offset = base_height
            z_offset += (mean_pop / 200.0) # Base lift
            z_offset += wave * (std_pop / 20.0) # Amplitude based on StdDev
            
            x = current_ring_radius * math.cos(angle)
            y = current_ring_radius * math.sin(angle)
            
            # Clip to simple cylinder wall at the edge
            if r == rings:
                z_offset = base_height # Force edge to match wall
            
            current_ring_indices.append(add_vert(x, y, z_offset))
            
        # Stich ring to previous ring
        for s in range(segments):
            # Previous ring verts
            p1 = prev_ring_indices[s]
            p2 = prev_ring_indices[(s + 1) % segments]
            
            # Current ring verts
            c1 = current_ring_indices[s]
            c2 = current_ring_indices[(s + 1) % segments]
            
            # If r=1, p1 and p2 are the same (center point), so we just make triangles
            if r == 1:
                faces.append((p1, c1, c2))
            else:
                # Quads to tris
                faces.append((p1, c1, c2))
                faces.append((p1, c2, p2))
                
        prev_ring_indices = current_ring_indices

    # 5. Write Output
    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pc_token_gen.py <input.json> <output.stl>")
    else:
        generate_pc_token(sys.argv[1], sys.argv[2])
