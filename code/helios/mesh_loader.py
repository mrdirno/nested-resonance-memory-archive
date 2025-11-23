"""
HELIOS Mesh Loader
Part of the "Architect" Phase.
Parses .obj files and converts them into voxel targets for the Universal Operator.
"""
import numpy as np
import random

class MeshLoader:
    """
    A standalone OBJ parser and voxelizer.
    Does not require external heavy libraries (trimesh, etc).
    """
    def __init__(self):
        pass

    def load_obj(self, filepath: str):
        """
        Parses a standard .obj file.
        Returns vertices (list of np.array) and faces (list of list of int indices).
        """
        vertices = []
        faces = []
        
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                
                if values[0] == 'v':
                    v = np.array([float(x) for x in values[1:4]])
                    vertices.append(v)
                elif values[0] == 'f':
                    # Handle face formats like 1/1/1 or 1//1
                    # We only care about the vertex index (first number)
                    face_indices = []
                    for v_str in values[1:]:
                        v_idx = int(v_str.split('/')[0])
                        # OBJ is 1-indexed, convert to 0-indexed
                        face_indices.append(v_idx - 1)
                    faces.append(face_indices)
                    
        return vertices, faces

    def voxelize_surface(self, vertices, faces, resolution_mm: float):
        """
        Generates a point cloud representing the surface of the mesh.
        Uses Monte Carlo sampling on triangle faces.
        """
        points = []
        
        # 1. Calculate total area to determine point density? 
        # Simpler: Ensure point spacing approx equals resolution_mm
        # Area of triangle ~ 0.5 * base * height.
        # Number of points ~ Area / (resolution_mm^2)
        
        for face in faces:
            if len(face) < 3: continue # Skip lines/points
            
            # Triangulate polygons (simple fan method)
            v0 = vertices[face[0]]
            for i in range(1, len(face)-1):
                v1 = vertices[face[i]]
                v2 = vertices[face[i+1]]
                
                self._sample_triangle(v0, v1, v2, resolution_mm, points)
                
        # Remove duplicates (if any vertices were explicitly added) and simple cleanup
        # For now, just return unique list
        return points

    def _sample_triangle(self, v0, v1, v2, resolution, point_list):
        """
        Populates a triangle with points separated by roughly 'resolution'.
        """
        # Calculate Area
        cross_prod = np.cross(v1 - v0, v2 - v0)
        area = 0.5 * np.linalg.norm(cross_prod)
        
        # Target point count
        # Area / (res * res) gives roughly correct density
        target_count = int(area / (resolution * resolution))
        if target_count < 1: target_count = 1 # Always keep at least one point (centroid)
        
        # Monte Carlo sampling
        # P = (1 - sqrt(r1)) * A + (sqrt(r1) * (1 - r2)) * B + (sqrt(r1) * r2) * C
        for _ in range(target_count):
            r1 = random.random()
            r2 = random.random()
            
            sqrt_r1 = np.sqrt(r1)
            
            a_coeff = 1.0 - sqrt_r1
            b_coeff = sqrt_r1 * (1.0 - r2)
            c_coeff = sqrt_r1 * r2
            
            point = a_coeff * v0 + b_coeff * v1 + c_coeff * v2
            point_list.append(point)

    def center_and_scale(self, vertices, target_scale_mm=50.0):
        """
        Utilities to fit the mesh into the simulation box.
        Returns modified vertices.
        """
        verts = np.array(vertices)
        
        # Center
        centroid = np.mean(verts, axis=0)
        verts -= centroid
        
        # Scale
        # Find max dimension
        max_dim = np.max(np.max(verts, axis=0) - np.min(verts, axis=0))
        if max_dim > 0:
            scale_factor = target_scale_mm / max_dim
            verts *= scale_factor
            
        # Move to center of box (assuming box is 0..100) -> 50,50,50
        verts += np.array([50.0, 50.0, 50.0])
        
        return [v for v in verts] # Return as list of arrays

if __name__ == "__main__":
    # Test Bench
    loader = MeshLoader()
    
    # Create a dummy OBJ file for testing (Tetrahedron)
    with open("test_tetra.obj", "w") as f:
        f.write("v 10 10 10\n")
        f.write("v 20 10 10\n")
        f.write("v 15 20 10\n")
        f.write("v 15 15 20\n")
        f.write("f 1 2 3\n")
        f.write("f 1 2 4\n")
        f.write("f 2 3 4\n")
        f.write("f 3 1 4\n")
        
    print("Loading test_tetra.obj...")
    verts, faces = loader.load_obj("test_tetra.obj")
    print(f"Vertices: {len(verts)}, Faces: {len(faces)}")
    
    print("Centering...")
    verts = loader.center_and_scale(verts, target_scale_mm=20.0)
    print(f"New Center: {verts[0]}")
    
    print("Voxelizing...")
    targets = loader.voxelize_surface(verts, faces, resolution_mm=2.0)
    print(f"Generated Targets: {len(targets)}")
    
    import os
    os.remove("test_tetra.obj")
    print("Test Complete.")
