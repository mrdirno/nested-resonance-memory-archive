import numpy as np
import math
import sys

def write_stl(filename, vertices, faces):
    """
    Writes a mesh to an ASCII STL file.
    vertices: List of (x, y, z) coordinates.
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

def generate_osd_isosurface(output_path, resolution=120):
    """
    Generates a 3D mesh representing the "Orthogonal Sum Dynamics" field.
    We use the Gyroid approximation as a stable, printable representation 
    of infinite standing wave interference.
    
    Equation: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) > threshold
    """
    print(f"Generating OSD Resonance Field: {output_path}")
    
    # Grid Parameters
    size = 40.0  # mm cube
    scale = 2.0 * math.pi / (size / 3.0) # 3 periods across the cube
    
    # Marching Cubes (Simplified: Voxel Surface Extraction)
    # We will iterate through the grid, find surface voxels, and create quads/tris.
    # This is 'blocky' but robust without external libs.
    
    step = size / resolution
    vertices = []
    faces = []
    
    # 3D Array of field values
    # True if solid (Constructive Interference), False if empty (Destructive)
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Field Interference...")
    for x in range(resolution):
        for y in range(resolution):
            for z in range(resolution):
                # Map grid to spatial coords
                px = (x * step) - (size/2)
                py = (y * step) - (size/2)
                pz = (z * step) - (size/2)
                
                # OSD Gyroid Equation
                # V(x) ~ sum of waves. 
                val = math.sin(px * scale) * math.cos(py * scale) + \
                      math.sin(py * scale) * math.cos(pz * scale) + \
                      math.sin(pz * scale) * math.cos(px * scale)
                
                # Threshold determines wall thickness
                # Close to 0 = thin walls. > 0.2 or < -0.2 = thicker.
                # We want a solid shell.
                if abs(val) < 0.4: 
                    grid[x,y,z] = True

    # Extract Surface Mesh
    # For every solid voxel, check neighbors. If neighbor is empty, add a face.
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2)) # Tri 1
        faces.append((idx, idx+2, idx+3)) # Tri 2

    for x in range(resolution):
        for y in range(resolution):
            for z in range(resolution):
                if not grid[x,y,z]:
                    continue
                
                # Voxel center coords
                vx = (x * step)
                vy = (y * step)
                vz = (z * step)
                s2 = step / 2
                
                # Neighbors (Up, Down, Left, Right, Front, Back)
                # If neighbor is out of bounds or False, draw face
                
                # X+ Face
                if x == resolution-1 or not grid[x+1,y,z]:
                    add_quad((vx+s2, vy-s2, vz-s2), (vx+s2, vy+s2, vz-s2), (vx+s2, vy+s2, vz+s2), (vx+s2, vy-s2, vz+s2))
                # X- Face
                if x == 0 or not grid[x-1,y,z]:
                    add_quad((vx-s2, vy-s2, vz+s2), (vx-s2, vy+s2, vz+s2), (vx-s2, vy+s2, vz-s2), (vx-s2, vy-s2, vz-s2))
                    
                # Y+ Face
                if y == resolution-1 or not grid[x,y+1,z]:
                    add_quad((vx+s2, vy+s2, vz-s2), (vx-s2, vy+s2, vz-s2), (vx-s2, vy+s2, vz+s2), (vx+s2, vy+s2, vz+s2))
                # Y- Face
                if y == 0 or not grid[x,y-1,z]:
                    add_quad((vx-s2, vy-s2, vz-s2), (vx+s2, vy-s2, vz-s2), (vx+s2, vy-s2, vz+s2), (vx-s2, vy-s2, vz+s2))

                # Z+ Face
                if z == resolution-1 or not grid[x,y,z+1]:
                    add_quad((vx+s2, vy-s2, vz+s2), (vx+s2, vy+s2, vz+s2), (vx-s2, vy+s2, vz+s2), (vx-s2, vy-s2, vz+s2))
                # Z- Face
                if z == 0 or not grid[x,y,z-1]:
                    add_quad((vx-s2, vy-s2, vz-s2), (vx-s2, vy+s2, vz-s2), (vx+s2, vy+s2, vz-s2), (vx+s2, vy-s2, vz-s2))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_field_gen.py <output.stl>")
    else:
        generate_osd_isosurface(sys.argv[1])
