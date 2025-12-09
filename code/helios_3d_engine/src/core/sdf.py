import numpy as np
from scipy.ndimage import distance_transform_edt

class SDFEngine:
    def __init__(self):
        pass

    def gyroid(self, x, y, z, scale=1.0, thickness=0.1):
        x = x * scale
        y = y * scale
        z = z * scale
        val = np.sin(x)*np.cos(y) + np.sin(y)*np.cos(z) + np.sin(z)*np.cos(x)
        return np.abs(val) - thickness

    def sphere(self, x, y, z, radius=1.0):
        return np.sqrt(x**2 + y**2 + z**2) - radius

    def box(self, x, y, z, size=1.0):
        q = np.abs(np.stack([x,y,z])) - size
        return np.linalg.norm(np.maximum(q, 0.0), axis=0) + np.minimum(np.max(q, axis=0), 0.0)

    def union(self, d1, d2):
        return np.minimum(d1, d2)

    def difference(self, d1, d2):
        return np.maximum(d1, -d2)

    def intersection(self, d1, d2):
        return np.maximum(d1, d2)

    def smooth_union(self, d1, d2, k=0.1):
        h = np.clip(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0)
        return np.mix(d2, d1, h) - k * h * (1.0 - h)

    def voxels_to_sdf(self, voxels):
        """
        Converts a binary voxel grid (True=Inside) to a Signed Distance Field.
        Returns: SDF grid (Negative inside, Positive outside)
        """
        # EDT calculates distance to nearest 0 (Background)
        # Inside: Dist to background
        # Outside: Dist to foreground
        
        # Invert voxels for EDT: 0=Inside, 1=Outside
        bg_dist = distance_transform_edt(voxels) # Dist from inside to boundary
        fg_dist = distance_transform_edt(~voxels) # Dist from outside to boundary
        
        # SDF: Negative inside, Positive outside
        # Normalize? EDT returns pixel units.
        
        sdf = fg_dist - bg_dist
        return sdf