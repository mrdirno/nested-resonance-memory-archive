import math
import numpy as np
from scipy import ndimage

class AGPHCore:
    def __init__(self, 
                 scale_x=1.0, scale_y=1.0, scale_z=1.0,
                 twist_rate=0.0, 
                 anisotropy=(1.0, 1.0, 1.0),
                 gyroid_thickness=0.2):
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z
        self.twist_rate = twist_rate 
        self.anisotropy = np.array(anisotropy)
        self.thickness = gyroid_thickness

    def transform(self, x, y, z, macro_scale_factor=1.0):
        sx = x / macro_scale_factor
        sy = y / macro_scale_factor
        sz = z 
        
        theta = z * self.twist_rate
        cos_t = math.cos(-theta)
        sin_t = math.sin(-theta)
        
        rx = sx * cos_t - sy * sin_t
        ry = sx * sin_t + sy * cos_t
        rz = sz
        
        tx = rx * self.scale_x * self.anisotropy[0]
        ty = ry * self.scale_y * self.anisotropy[1]
        tz = rz * self.scale_z * self.anisotropy[2]
        
        return tx, ty, tz

    def evaluate_gyroid(self, tx, ty, tz):
        return math.sin(tx)*math.cos(ty) + math.sin(ty)*math.cos(tz) + math.sin(tz)*math.cos(tx)

    def get_field_value(self, x, y, z, macro_scale_factor=1.0):
        tx, ty, tz = self.transform(x, y, z, macro_scale_factor)
        return self.evaluate_gyroid(tx, ty, tz)

    def is_solid(self, val):
        return abs(val) < self.thickness

def morphological_cleanup(grid):
    """
    Applies binary closing to bridge small gaps and remove noise.
    """
    print("  -> Applying Morphological Closing (bridge gaps)...")
    # Structure: 3x3x3 connectivity
    struct = ndimage.generate_binary_structure(3, 1) 
    # Closing = Dilation then Erosion
    closed_grid = ndimage.binary_closing(grid, structure=struct, iterations=1)
    return closed_grid