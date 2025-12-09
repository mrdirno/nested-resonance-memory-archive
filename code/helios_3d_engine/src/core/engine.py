import numpy as np
from skimage.measure import marching_cubes
from .sdf import gyroid, sphere, intersect

class GeometryEngine:
    def __init__(self):
        pass

    def generate_gyroid_mesh(self, resolution=64, scale=2.0, thickness=0.1):
        # Create grid
        x = np.linspace(-np.pi, np.pi, resolution)
        y = np.linspace(-np.pi, np.pi, resolution)
        z = np.linspace(-np.pi, np.pi, resolution)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Evaluate SDF
        # Compose: Sphere intersected with Gyroid
        d_sphere = sphere(X, Y, Z, radius=2.5)
        d_gyroid = gyroid(X, Y, Z, scale=scale, thickness=thickness)
        
        # d_final = intersect(d_sphere, d_gyroid)
        d_final = d_gyroid # Let's see pure gyroid first inside the box
        
        # Marching Cubes
        try:
            verts, faces, normals, values = marching_cubes(d_final, level=0.0)
            
            # Normalize verts to -1..1 range for rendering
            # Grid size is 2*pi
            range_val = 2 * np.pi
            verts = (verts / (resolution - 1)) * range_val - np.pi
            
import struct

    @staticmethod
    def save_stl(filename, verts, faces, normals=None):
        """
        Saves the mesh to a binary STL file.
        """
        with open(filename, 'wb') as f:
            # 80 byte header
            f.write(b'\0' * 80)
            
            # Number of triangles
            count = len(faces)
            f.write(struct.pack('<I', count))
            
            # Triangles
            # STL format: Normal (3f), V1 (3f), V2 (3f), V3 (3f), Attribute (2b)
            # We iterate. For speed, we could vectorize this, but Python loop is okay for <100k tris.
            # If normals are provided, we use face normal (or average). 
            # Standard STL expects one normal per triangle.
            
            for face in faces:
                v1 = verts[face[0]]
                v2 = verts[face[1]]
                v3 = verts[face[2]]
                
                # Calculate normal if not provided
                # simple cross product
                edge1 = v2 - v1
                edge2 = v3 - v1
                norm = np.cross(edge1, edge2)
                norm_len = np.linalg.norm(norm)
                if norm_len > 0:
                    norm /= norm_len
                else:
                    norm = np.array([0,0,1])
                
                # Write
                data = struct.pack('<12fH', 
                    norm[0], norm[1], norm[2],
                    v1[0], v1[1], v1[2],
                    v2[0], v2[1], v2[2],
                    v3[0], v3[1], v3[2],
                    0
                )
                f.write(data)
