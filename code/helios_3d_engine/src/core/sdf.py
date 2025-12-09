import numpy as np
from .sdf import gyroid, sphere, box, union, intersect, difference

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
