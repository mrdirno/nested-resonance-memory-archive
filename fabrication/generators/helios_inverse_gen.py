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

def generate_inverse_gyroid(output_path, size_x=40.0, size_y=40.0, size_z=40.0, resolution=120):
    """
    Generates 'The Void': The Inverse Gyroid.
    Logic: The region complementary to the Gyroid wall (abs(val) >= threshold).
    """
    print(f"Generating Inverse Gyroid: {output_path}")
    
    # Same scale as Artifact 01 for compatibility
    scale_x = 2.0 * math.pi / (size_x / 3.0)
    scale_y = 2.0 * math.pi / (size_y / 3.0)
    scale_z = 2.0 * math.pi / (size_z / 3.0)
    
    step_x = size_x / resolution
    step_y = size_y / resolution
    step_z = size_z / resolution
    
    vertices = []
    faces = []
    
    # Create grid
    x_range = np.linspace(-size_x/2, size_x/2, resolution)
    y_range = np.linspace(-size_y/2, size_y/2, resolution)
    z_range = np.linspace(-size_z/2, size_z/2, resolution)
    
    # 3D Boolean Grid
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Inverse Field...")
    
    for ix, x in enumerate(x_range):
        for iy, y in enumerate(y_range):
            for iz, z in enumerate(z_range):
                
                # Standard Gyroid Equation
                val = math.sin(x * scale_x) * math.cos(y * scale_y) + \
                      math.sin(y * scale_y) * math.cos(z * scale_z) + \
                      math.sin(z * scale_z) * math.cos(x * scale_x)
                
                # THE INVERSION:
                # Gyroid Walls: abs(val) < 0.4
                # Inverse: abs(val) >= 0.4 (Everything NOT the Wall)
                # This ensures that when overlaid with a standard Gyroid, the result is a solid block.
                
                if abs(val) >= 0.4: 
                    grid[ix, iy, iz] = True

    # Extract Surface
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Standard voxel face extraction
    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                vx = x_range[x_idx]
                vy = y_range[y_idx]
                vz = z_range[z_idx]
                s2x = step_x / 2
                s2y = step_y / 2
                s2z = step_z / 2
                
                # Neighbors
                if x_idx == resolution-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                
                if y_idx == resolution-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))

                if z_idx == resolution-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_inverse_gen.py <output.stl> [size_x] [size_y] [size_z] [resolution]")
    else:
        output_file = sys.argv[1]
        
        # Default values
        params = {
            "size_x": 40.0,
            "size_y": 40.0,
            "size_z": 40.0,
            "resolution": 120
        }
        
        # Parse optional arguments
        if len(sys.argv) > 2: params["size_x"] = float(sys.argv[2])
        if len(sys.argv) > 3: params["size_y"] = float(sys.argv[3])
        if len(sys.argv) > 4: params["size_z"] = float(sys.argv[4])
        if len(sys.argv) > 5: params["resolution"] = int(sys.argv[5])

        generate_inverse_gyroid(output_file, **params)
