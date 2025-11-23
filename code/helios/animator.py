"""
HELIOS Animator
The Engine for Dynamic Topology (4D Printing).
Interpolates between two point clouds to generate a frame sequence.
"""
import numpy as np
from scipy.spatial.distance import cdist

class Animator:
    def __init__(self):
        pass

    def interpolate(self, start_points, end_points, frames):
        """
        Generates a sequence of point clouds morphing from start to end.
        Uses nearest neighbor mapping to handle point count mismatches.
        """
        start_arr = np.array(start_points)
        end_arr = np.array(end_points)
        
        # 1. Map points
        # If counts differ, we need to map each start point to a target end point.
        # We can use Nearest Neighbor for simplicity.
        # For a smooth morph, optimal transport is better but expensive.
        # Let's stick to a simple heuristic:
        # For each start point, find closest end point.
        # If end has more points, map extra end points to closest start point (appear from it).
        
        # Actually, for physical particles, conservation of mass implies particle count should be constant
        # or particles move in/out of field.
        # The simulator assumes fixed emitters but "virtual" particles.
        # The *targets* are just points where we want high pressure nodes.
        # We can just interpolate the targets.
        
        # Simple Linear Interpolation (Lerp) requires matched arrays.
        # Strategy: Resample both to same count? Or just match closest?
        
        # Let's map Start -> End.
        dist_matrix = cdist(start_arr, end_arr)
        # mapping[i] = index of end point closest to start[i]
        mapping_indices = np.argmin(dist_matrix, axis=1)
        mapped_end = end_arr[mapping_indices]
        
        # This leaves some end points unused if start > end, or multiple start -> single end.
        # It handles the "shape A morphs to shape B" visually.
        
        trajectory = []
        for f in range(frames):
            t = f / (frames - 1) if frames > 1 else 1.0
            # Linear interpolation
            current_points = (1 - t) * start_arr + t * mapped_end
            trajectory.append(current_points)
            
        return trajectory

if __name__ == "__main__":
    # Test
    start = [[0,0,0], [10,0,0], [0,10,0]] # Triangle
    end = [[0,0,0], [10,0,0], [0,10,0], [5,5,10]] # Pyramid (4 points)
    # Note: This naive mapper will ignore the 4th point of the pyramid if count mismatches.
    # A better approach for the Operator is to regenerate targets for each frame 
    # based on a parametric definition, BUT for arbitrary meshes, point matching is hard.
    
    # Alternative: Voxelize the *interpolated mesh*? No, we have point clouds.
    # Refined Strategy: 
    # 1. Force equal point counts during voxelization?
    # 2. Just use the mapping above for V1.
    
    anim = Animator()
    frames = anim.interpolate(start, end, 5)
    print(f"Generated {len(frames)} frames.")
    print(f"Frame 0: {frames[0]}")
    print(f"Frame 4: {frames[4]}")
