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
        d_final = d_gyroid # Pure gyroid for now
        
        # Marching Cubes
        try:
            verts, faces, normals, values = marching_cubes(d_final, level=0.0)
            
            # Normalize verts to -1..1 range
            range_val = 2 * np.pi
            verts = (verts / (resolution - 1)) * range_val - np.pi
            
            return verts, normals, faces
            
        except RuntimeError:
            print("No surface found at level 0.0")
            return None, None, None
            
    @staticmethod
    def save_stl(filename, verts, faces, normals=None):
        import struct
        with open(filename, 'wb') as f:
            f.write(b'\0' * 80)
            count = len(faces)
            f.write(struct.pack('<I', count))
            for face in faces:
                v1 = verts[face[0]]
                v2 = verts[face[1]]
                v3 = verts[face[2]]
                # Simple normal calc if needed, or use provided
                norm = np.array([0,0,1]) # Placeholder if not calc
                data = struct.pack('<12fH', norm[0], norm[1], norm[2],
                    v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2], 0)
                f.write(data)
