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
            
            return verts, normals, faces
            
        except RuntimeError:
            print("No surface found at level 0.0")
            return None, None, None
