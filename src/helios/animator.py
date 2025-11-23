"""
HELIOS Animator
Phase 11: Dynamic Topology
Interpolates between 3D meshes to create 4D printing sequences.
"""
import numpy as np
import copy
from src.helios.mesh_loader import MeshLoader

class Animator:
    def __init__(self):
        self.loader = MeshLoader()
        
    def load_keyframe(self, filepath: str, scale_mm=50.0):
        """
        Loads a mesh keyframe.
        Returns vertices and faces.
        """
        verts, faces = self.loader.load_obj(filepath)
        verts = self.loader.center_and_scale(verts, target_scale_mm=scale_mm)
        return np.array(verts), faces
        
    def interpolate(self, start_mesh, end_mesh, frames: int):
        """
        Generates a sequence of point clouds (targets) interpolating between start and end meshes.
        start_mesh: (verts_a, faces_a)
        end_mesh: (verts_b, faces_b)
        """
        verts_a, faces_a = start_mesh
        verts_b, faces_b = end_mesh
        
        # 1. Map vertices for morphing
        # Strategy: "Greedy Flow"
        # We cannot easily change topology (faces) continuously without complex remeshing.
        # Simplification: We will morph the *point cloud* directly? 
        # No, we want to voxelize the intermediate surface.
        # 
        # Hybrid Approach:
        # We will treat the transition as a "Cloud Morph".
        # We generate a high-res point cloud for A and B.
        # Then we map points in Cloud A to Cloud B.
        # Then we interpolate the points.
        
        # A. Voxelize both keyframes to get dense point clouds
        cloud_a = self.loader.voxelize_surface(verts_a, faces_a, resolution_mm=2.0)
        cloud_b = self.loader.voxelize_surface(verts_b, faces_b, resolution_mm=2.0)
        
        cloud_a = np.array(cloud_a)
        cloud_b = np.array(cloud_b)
        
        # B. Match points (Nearest Neighbor)
        # For each point in A, find target in B
        # If len(A) != len(B), we handle mismatch.
        
        # Make them equal size by resampling?
        # Let's just map A->B and B->A and blend?
        # Simpler: Resample the smaller cloud to match the larger one by duplicating points?
        # Or just use the larger size.
        
        target_size = max(len(cloud_a), len(cloud_b))
        
        # Resample A
        indices_a = np.random.choice(len(cloud_a), target_size, replace=True)
        resampled_a = cloud_a[indices_a]
        
        # Resample B
        indices_b = np.random.choice(len(cloud_b), target_size, replace=True)
        resampled_b = cloud_b[indices_b]
        
        # Sort/Match to minimize travel distance (Linear Assignment approximation)
        # Full Hungarian algo is O(N^3), too slow.
        # Greedy sort by spatial index (e.g., Z-coordinate, then Y, then X)
        # This keeps nearby points roughly together in the list.
        
        # Lexsort keys: (x, y, z)
        order_a = np.lexsort((resampled_a[:,0], resampled_a[:,1], resampled_a[:,2]))
        sorted_a = resampled_a[order_a]
        
        order_b = np.lexsort((resampled_b[:,0], resampled_b[:,1], resampled_b[:,2]))
        sorted_b = resampled_b[order_b]
        
        # C. Generate Frames
        sequence = []
        for i in range(frames):
            t = i / float(frames - 1) # 0.0 to 1.0
            
            # Linear Interpolation
            current_cloud = (1.0 - t) * sorted_a + t * sorted_b
            
            # Convert back to list of arrays
            sequence.append([p for p in current_cloud])
            
        return sequence

    def generate_sequence(self, operator, targets_sequence):
        """
        Solves phases for each frame in the sequence.
        Returns list of phase arrays.
        """
        phase_sequence = []
        print(f"Compiling {len(targets_sequence)} frames...")
        
        for i, targets in enumerate(targets_sequence):
            print(f"  Frame {i+1}/{len(targets_sequence)}: {len(targets)} points")
            phases = operator._solve_phases(targets)
            phase_sequence.append(phases)
            
        return phase_sequence
