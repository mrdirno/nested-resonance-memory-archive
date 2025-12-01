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

def generate_gradient_sphere(output_path, resolution=150, diameter=100.0):
    """
    Generates 'The Gradient Well': A Spherical Gyroid with radial density fade.
    """
    print(f"Generating Artifact 02: The Gradient Well ({output_path})")
    
    radius = diameter / 2.0
    scale = 2.0 * math.pi / (diameter / 4.0) # 4 periods across diameter
    
    step = diameter / resolution
    vertices = []
    faces = []
    
    # Create grid
    x_range = np.linspace(-radius, radius, resolution)
    y_range = np.linspace(-radius, radius, resolution)
    z_range = np.linspace(-radius, radius, resolution)
    
    # 3D Boolean Grid
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Gradient Field...")
    
    for ix, x in enumerate(x_range):
        for iy, y in enumerate(y_range):
            for iz, z in enumerate(z_range):
                
                # 1. Global Spherical Mask
                dist = math.sqrt(x*x + y*y + z*z)
                if dist > radius:
                    continue # Cut everything outside sphere
                
                # 2. The Gyroid Field
                gyroid = math.sin(x * scale) * math.cos(y * scale) + \
                         math.sin(y * scale) * math.cos(z * scale) + \
                         math.sin(z * scale) * math.cos(x * scale)
                
                # 3. The Bias (Gradient)
                # We want the core to be thicker/solid, and the edge to be thinner/airy.
                # Normalized distance (0 at center, 1 at edge)
                d_norm = dist / radius
                
                # Threshold Function: 
                # At center (d=0), we accept a wider range (thicker walls).
                # At edge (d=1), we accept a narrower range (thinner walls).
                # Base thickness: 0.8. Fade to: 0.1.
                
                thickness_threshold = 0.9 - (0.8 * d_norm) 
                
                # If gyroid value is within the "accepted" thickness slice
                if abs(gyroid) < thickness_threshold:
                    grid[ix, iy, iz] = True

    # Extract Surface (Simplified Marching Cubes - Voxel Face)
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
                
                # Center of voxel
                vx = x_range[x]
                vy = y_range[y]
                vz = z_range[z]
                s2 = step / 2
                
                # Neighbors
                if x == resolution-1 or not grid[x+1,y,z]:
                    add_quad((vx+s2, vy-s2, vz-s2), (vx+s2, vy+s2, vz-s2), (vx+s2, vy+s2, vz+s2), (vx+s2, vy-s2, vz+s2))
                if x == 0 or not grid[x-1,y,z]:
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
        print("Usage: python helios_gradient_gen.py <output.stl>")
    else:
        generate_gradient_sphere(sys.argv[1])
