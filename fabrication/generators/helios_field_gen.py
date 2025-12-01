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

def generate_osd_isosurface(output_path, size_x=40.0, size_y=40.0, size_z=40.0, resolution=120):
    """
    Generates a 3D mesh representing the "Orthogonal Sum Dynamics" field.
    We use the Gyroid approximation as a stable, printable representation 
    of infinite standing wave interference.
    
    Equation: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) > threshold
    """
    print(f"Generating OSD Resonance Field: {output_path}")
    
    # Grid Parameters
    scale_x = 2.0 * math.pi / (size_x / 3.0) # 3 periods across X
    scale_y = 2.0 * math.pi / (size_y / 3.0) # 3 periods across Y
    scale_z = 2.0 * math.pi / (size_z / 3.0) # 3 periods across Z
    
    # Marching Cubes (Simplified: Voxel Surface Extraction)
    step_x = size_x / resolution
    step_y = size_y / resolution
    step_z = size_z / resolution
    
    vertices = []
    faces = []
    
    # 3D Array of field values
    # True if solid (Constructive Interference), False if empty (Destructive)
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Field Interference...")
    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                # Map grid to spatial coords
                px = (x_idx * step_x) - (size_x/2)
                py = (y_idx * step_y) - (size_y/2)
                pz = (z_idx * step_z) - (size_z/2)
                
                # OSD Gyroid Equation
                val = math.sin(px * scale_x) * math.cos(py * scale_y) + \
                      math.sin(py * scale_y) * math.cos(pz * scale_z) + \
                      math.sin(pz * scale_z) * math.cos(px * scale_x)
                
                # Threshold determines wall thickness
                if abs(val) < 0.4: 
                    grid[x_idx,y_idx,z_idx] = True

    # Extract Surface Mesh
    # For every solid voxel, check neighbors. If neighbor is empty, add a face.
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2)) # Tri 1
        faces.append((idx, idx+2, idx+3)) # Tri 2

    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                # Voxel center coords
                vx = (x_idx * step_x) - (size_x/2)
                vy = (y_idx * step_y) - (size_y/2)
                vz = (z_idx * step_z) - (size_z/2)
                s2x = step_x / 2
                s2y = step_y / 2
                s2z = step_z / 2
                
                # Neighbors (Up, Down, Left, Right, Front, Back)
                # If neighbor is out of bounds or False, draw face
                
                # X+ Face
                if x_idx == resolution-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                # X- Face
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                    
                # Y+ Face
                if y_idx == resolution-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                # Y- Face
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))

                # Z+ Face
                if z_idx == resolution-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                # Z- Face
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_field_gen.py <output.stl> [size_x] [size_y] [size_z] [resolution]")
    else:
        output_file = sys.argv[1]
        
        # Default values for a cube
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

        generate_osd_isosurface(output_file, **params)
