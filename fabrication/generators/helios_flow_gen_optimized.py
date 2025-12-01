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

def generate_optimized_prism(output_path, resolution=100, size_x=60.0, size_z=120.0):
    """
    Generates 'The Directional Current' (Artifact 03) - OPTIMIZED VERSION
    Target: Unit Cell Size (L) approx 15mm.
    Original was ~40/3 = 13.3mm.
    We want coarser cells for easier printing.
    New Scale: 2.0 * pi / (size_x / 4.0) -> 15mm cells across 60mm width.
    """
    print(f"Generating Artifact 03: OPTIMIZED ({output_path})")
    
    # Optimized Frequency: 4 cells across 60mm = 15mm per cell.
    # This is the "Sweet Spot" from our analysis.
    base_scale = 2.0 * math.pi / (size_x / 4.0) 
    
    step_x = size_x / resolution
    step_y = size_x / resolution
    step_z = size_z / (resolution * 2)
    
    vertices = []
    faces = []
    
    # Create grid
    x_range = np.linspace(-size_x/2, size_x/2, resolution)
    y_range = np.linspace(-size_x/2, size_x/2, resolution)
    z_range = np.linspace(-size_z/2, size_z/2, resolution * 2)
    
    # 3D Boolean Grid
    grid = np.zeros((resolution, resolution, resolution * 2), dtype=bool)
    
    print("Calculating Optimized Flow Field...")
    
    for iz, z in enumerate(z_range):
        # Same flow logic, just applied to the coarser mesh
        z_norm = (z + size_z/2) / size_z
        freq_mod = 1.0 + (z_norm * 2.0) 
        z_prime = z / freq_mod
        
        for ix, x in enumerate(x_range):
            for iy, y in enumerate(y_range):
                
                gyroid = math.sin(x * base_scale) * math.cos(y * base_scale) + \
                         math.sin(y * base_scale) * math.cos(z_prime * base_scale) + \
                         math.sin(z_prime * base_scale) * math.cos(x * base_scale)
                
                # Slightly thicker walls (0.5 threshold) for robustness
                if abs(gyroid) < 0.5:
                    grid[ix, iy, iz] = True

    # Extract Surface
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Standard extraction
    for x in range(resolution):
        for y in range(resolution):
            for z in range(resolution * 2):
                if not grid[x,y,z]:
                    continue
                
                vx = x_range[x]
                vy = y_range[y]
                vz = z_range[z]
                sx2 = step_x / 2
                sy2 = step_y / 2
                sz2 = step_z / 2
                
                # Neighbors check (simplified)
                if x == resolution-1 or not grid[x+1,y,z]:
                    add_quad((vx+sx2, vy-sy2, vz-sz2), (vx+sx2, vy+sy2, vz-sz2), (vx+sx2, vy+sy2, vz+sz2), (vx+sx2, vy-sy2, vz+sz2))
                if x == 0 or not grid[x-1,y,z]:
                    add_quad((vx-sx2, vy-sy2, vz+sz2), (vx-sx2, vy+sy2, vz+sz2), (vx-sx2, vy+sy2, vz-sz2), (vx-sx2, vy-sy2, vz-sz2))
                if y == resolution-1 or not grid[x,y+1,z]:
                    add_quad((vx+sx2, vy+sy2, vz-sz2), (vx-sx2, vy+sy2, vz-sz2), (vx-sx2, vy+sy2, vz+sz2), (vx+sx2, vy+sy2, vz+sz2))
                if y == 0 or not grid[x,y-1,z]:
                    add_quad((vx-sx2, vy-sy2, vz-sz2), (vx+sx2, vy-sy2, vz-sz2), (vx+sx2, vy-sy2, vz+sz2), (vx-sx2, vy-sy2, vz+sz2))
                if z == (resolution * 2)-1 or not grid[x,y,z+1]:
                    add_quad((vx+sx2, vy-sy2, vz+sz2), (vx+sx2, vy+sy2, vz+sz2), (vx-sx2, vy+sy2, vz+sz2), (vx-sx2, vy-sy2, vz+sz2))
                if z == 0 or not grid[x,y,z-1]:
                    add_quad((vx-sx2, vy-sy2, vz-sz2), (vx-sx2, vy+sy2, vz-sz2), (vx+sx2, vy+sy2, vz-sz2), (vx+sx2, vy-sy2, vz-sz2))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_flow_gen_optimized.py <output.stl>")
    else:
        generate_optimized_prism(sys.argv[1])
