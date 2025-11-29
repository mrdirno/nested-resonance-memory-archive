"""
HELIOS Voxelizer (Gate 3.1)
Converts 3D Wavefront .obj meshes into discrete Target Density Fields.

Principle: PRIN-DIGITAL-MATTER (Voxelization)
Author: MOG (Cycle 2341)
"""

import numpy as np
import os

class Voxelizer:
    def __init__(self, resolution=64):
        """
        Initialize the Voxelizer.
        :param resolution: Grid resolution (N x N x N).
        """
        self.resolution = resolution
        self.vertices = []
        self.faces = []
        self.grid = np.zeros((resolution, resolution, resolution), dtype=np.float32)

    def load_obj(self, file_path):
        """
        Parses a standard .obj file (vertices and faces).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"OBJ file not found: {file_path}")

        verts = []
        faces = []

        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    parts = line.strip().split()
                    verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('f '):
                    parts = line.strip().split()
                    # Handle "v/vt/vn" format by taking just the first index
                    face_idxs = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    if len(face_idxs) == 3:
                        faces.append(face_idxs)
                    elif len(face_idxs) == 4:
                        # Quad to 2 triangles
                        faces.append([face_idxs[0], face_idxs[1], face_idxs[2]])
                        faces.append([face_idxs[0], face_idxs[2], face_idxs[3]])

        self.vertices = np.array(verts)
        self.faces = np.array(faces)
        print(f"Loaded mesh: {len(self.vertices)} vertices, {len(self.faces)} faces.")
        self.normalize_mesh()

    def normalize_mesh(self):
        """
        Centers the mesh and scales it to fit within the unit sphere (0.0 to 1.0 normalized coordinates).
        Scales to 90% of grid size to leave padding.
        """
        if len(self.vertices) == 0:
            return

        # Center
        centroid = np.mean(self.vertices, axis=0)
        self.vertices -= centroid

        # Scale
        max_dist = np.max(np.linalg.norm(self.vertices, axis=1))
        if max_dist > 0:
            scale_factor = 0.45  # Leaves 10% padding (0.5 - 0.45)
            self.vertices /= max_dist
            self.vertices *= scale_factor
        
        # Shift to 0.5, 0.5, 0.5 center
        self.vertices += 0.5

    def sample_triangle(self, v0, v1, v2, num_samples):
        """
        Uniformly samples points on a triangle surface.
        """
        r1 = np.random.rand(num_samples, 1)
        r2 = np.random.rand(num_samples, 1)
        
        sqrt_r1 = np.sqrt(r1)
        
        # Barycentric coordinates
        A = 1 - sqrt_r1
        B = sqrt_r1 * (1 - r2)
        C = sqrt_r1 * r2
        
        return A * v0 + B * v1 + C * v2

    def voxelize(self, density=1.0, surface_samples=1000):
        """
        Converts the mesh into a voxel grid by sampling faces.
        :param density: Value to assign to occupied voxels.
        :param surface_samples: Number of samples per face (adjust based on resolution).
        :return: The voxel grid.
        """
        self.grid.fill(0)
        
        print("Voxelizing...")
        
        for face in self.faces:
            v0 = self.vertices[face[0]]
            v1 = self.vertices[face[1]]
            v2 = self.vertices[face[2]]
            
            # Calculate triangle area to optimize sample count? 
            # For prototype, fixed samples is safer/easier.
            
            points = self.sample_triangle(v0, v1, v2, surface_samples)
            
            # Map to grid coordinates
            grid_coords = (points * self.resolution).astype(int)
            
            # Clip to valid range
            grid_coords = np.clip(grid_coords, 0, self.resolution - 1)
            
            # Fill grid
            # Simple boolean fill:
            self.grid[grid_coords[:, 0], grid_coords[:, 1], grid_coords[:, 2]] = density

        return self.grid

    def save_field(self, output_path):
        """
        Saves the voxel grid as a .npy file.
        """
        np.save(output_path, self.grid)
        print(f"Saved density field to {output_path}")

if __name__ == "__main__":
    # Self-test
    print("Creating dummy pyramid...")
    with open("dummy_pyramid.obj", "w") as f:
        f.write("v 1 0 1\n")
        f.write("v 1 0 -1\n")
        f.write("v -1 0 1\n")
        f.write("v -1 0 -1\n")
        f.write("v 0 1.5 0\n")
        f.write("f 1 2 3\n")
        f.write("f 2 4 3\n")
        f.write("f 1 2 5\n")
        f.write("f 2 4 5\n")
        f.write("f 4 3 5\n")
        f.write("f 3 1 5\n")
    
    v = Voxelizer(resolution=32)
    v.load_obj("dummy_pyramid.obj")
    grid = v.voxelize()
    print(f"Non-zero voxels: {np.count_nonzero(grid)}")
    
    # Cleanup
    os.remove("dummy_pyramid.obj")

# [SPORE] ID: The Colony
