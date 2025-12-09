import numpy as np

# Functional Primitives
def gyroid(x, y, z, scale=1.0, thickness=0.1):
    return np.abs(np.sin(x*scale)*np.cos(y*scale) + np.sin(y*scale)*np.cos(z*scale) + np.sin(z*scale)*np.cos(x*scale)) - thickness

def sphere(x, y, z, radius=1.0):
    return np.sqrt(x**2 + y**2 + z**2) - radius

def box(x, y, z, size=1.0):
    # exact box sdf
    # d = max(abs(p) - b, 0)
    q_x = np.abs(x) - size
    q_y = np.abs(y) - size
    q_z = np.abs(z) - size
    return np.maximum(q_x, np.maximum(q_y, q_z))

def union(d1, d2):
    return np.minimum(d1, d2)

def intersect(d1, d2):
    return np.maximum(d1, d2)

def difference(d1, d2):
    return np.maximum(d1, -d2)

class SDFEngine:
    def __init__(self):
        pass

    def voxels_to_sdf(self, voxels):
        """
        Approximates an SDF from a binary voxel grid.
        Simple Signed Distance Transform: 
        - Inside = Negative distance to surface
        - Outside = Positive distance to surface
        """
        from scipy.ndimage import distance_transform_edt
        
        # Ensure voxels is numpy bool
        # voxels comes from PyTorch usually
        if hasattr(voxels, 'cpu'):
            v = voxels.cpu().numpy()
        else:
            v = voxels
            
        # Distance to nearest 0 (Background)
        # EDT computes distance to non-zero. 
        # So for inside points (1), we want distance to 0.
        # We invert logic: input to edt should be 0 for background.
        
        # Distance inside (negative)
        # edt(v) gives distance from 0s. So inside points get distance to boundary.
        dist_inside = distance_transform_edt(v)
        
        # Distance outside (positive)
        # edt(~v) gives distance from 1s. So outside points get distance to boundary.
        dist_outside = distance_transform_edt(~v)
        
        # Combine: SDF = dist_outside - dist_inside
        # If point is outside, dist_inside is 0. SDF > 0.
        # If point is inside, dist_outside is 0. SDF < 0.
        sdf = dist_outside - dist_inside
        
        # Normalize to [-1, 1] roughly if grid is normalized
        # But Marching Cubes usually handles arbitrary scale.
        
        return sdf

    # Wrapper for functional primitives
    def gyroid(self, x, y, z, scale=1.0, thickness=0.1):
        return gyroid(x, y, z, scale, thickness)

    def sphere(self, x, y, z, radius=1.0):
        return sphere(x, y, z, radius)
        
    def box(self, x, y, z, size=1.0):
        return box(x, y, z, size)

    def union(self, d1, d2):
        return union(d1, d2)

    def intersection(self, d1, d2):
        return intersect(d1, d2)

    def difference(self, d1, d2):
        return difference(d1, d2)
