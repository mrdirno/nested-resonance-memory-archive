import numpy as np
import math
import sys

def write_stl(filename, vertices, faces):
    """
    Writes a mesh to an ASCII STL file.
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

def generate_inverse_gyroid(output_path, resolution=120, size=40.0):
    """
    Generates 'The Void': The Inverse Gyroid (Channel B).
    Logic: Same equation, but we solidify the 'negative' space.
    """
    print(f"Generating Artifact 04: The Void ({output_path})")
    
    # Same scale as Artifact 01 for compatibility
    scale = 2.0 * math.pi / (size / 3.0) 
    
    step = size / resolution
    vertices = []
    faces = []
    
    # Create grid
    x_range = np.linspace(-size/2, size/2, resolution)
    y_range = np.linspace(-size/2, size/2, resolution)
    z_range = np.linspace(-size/2, size/2, resolution)
    
    # 3D Boolean Grid
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Inverse Field...")
    
    for ix, x in enumerate(x_range):
        for iy, y in enumerate(y_range):
            for iz, z in enumerate(z_range):
                
                # Standard Gyroid Equation
                val = math.sin(x * scale) * math.cos(y * scale) + \
                      math.sin(y * scale) * math.cos(z * scale) + \
                      math.sin(z * scale) * math.cos(x * scale)
                
                # THE INVERSION:
                # Artifact 01: abs(val) < 0.4 (The Wall)
                # Artifact 04: val > 0.4 (The Positive Void) OR val < -0.4 (The Negative Void)
                # To make it a single connected component (Channel B), we pick ONE side of the inequality.
                # Let's solidify the region where val > 0.4.
                # This creates the "Air" that fills one side of the Artifact 01 wall.
                
                if val > 0.4: 
                    grid[ix, iy, iz] = True

    # Extract Surface
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Standard voxel face extraction
    for x in range(resolution):
        for y in range(resolution):
            for z in range(resolution):
                if not grid[x,y,z]:
                    continue
                
                vx = x_range[x]
                vy = y_range[y]
                vz = z_range[z]
                s2 = step / 2
                
                # Neighbors
                if x == resolution-1 or not grid[x+1,y,z]:
                    add_quad((vx+s2, vy-s2, vz-s2), (vx+s2, vy+s2, vz-s2), (vx+s2, vy+s2, vz+s2), (vx+s2, vy-s2, vz+s2))
                if x == 0 or not grid[x-1,y,z]:
                    # Fixed typo in memory: all s2
                    add_quad((vx-s2, vy-s2, vz+s2), (vx-s2, vy+s2, vz+s2), (vx-s2, vy+s2, vz-s2), (vx-s2, vy-s2, vz-s2))
                
                if y == resolution-1 or not grid[x,y+1,z]:
                    add_quad((vx+s2, vy+s2, vz-s2), (vx-s2, vy+s2, vz-s2), (vx-s2, vy+s2, vz+s2), (vx+s2, vy+s2, vz+s2))
                if y == 0 or not grid[x,y-1,z]:
                    add_quad((vx-s2, vy-s2, vz-s2), (vx+s2, vy-s2, vz-s2), (vx+s2, vy-s2, vz+s2), (vx-s2, vy-s2, vz+s2))

                if z == resolution-1 or not grid[x,y,z+1]:
                    add_quad((vx+s2, vy-s2, vz+s2), (vx+s2, vy+s2, vz+s2), (vx-s2, vy+s2, vz+s2), (vx-s2, vy-s2, vz+s2))
                if z == 0 or not grid[x,y,z-1]:
                    add_quad((vx-s2, vy-s2, vz-s2), (vx-s2, vy+s2, vz-s2), (vx+s2, vy+s2, vz-s2), (vx+s2, vy-s2, vz-s2))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_inverse_gen.py <output.stl>")
    else:
        generate_inverse_gyroid(sys.argv[1])
