"""
HELIOS 3D Substrate Interface
Extension of the Substrate architecture for Volumetric compilation.
"""
from abc import ABC, abstractmethod
import numpy as np

class SubstrateInterface3D(ABC):
    """
    Abstract Base Class for 3D physical substrates.
    """
    
    def __init__(self, width: int, height: int, depth: int, wave_speed: float, damping: float):
        self.width = width
        self.height = height
        self.depth = depth
        self.wave_speed = wave_speed
        self.damping = damping
        
    @abstractmethod
    def propagate(self, emitters: list) -> np.ndarray:
        """
        Calculates the field in 3D space (x, y, z).
        Returns a 3D numpy array.
        """
        pass

class AcousticSubstrate3D(SubstrateInterface3D):
    """
    3D Acoustic Simulator.
    """
    def __init__(self, width_mm=50, height_mm=50, depth_mm=50, resolution_mm=1):
        w_pixels = int(width_mm / resolution_mm)
        h_pixels = int(height_mm / resolution_mm)
        d_pixels = int(depth_mm / resolution_mm)
        super().__init__(w_pixels, h_pixels, d_pixels, wave_speed=343.0, damping=0.001)
        self.resolution = resolution_mm
        
    def propagate(self, emitters: list) -> np.ndarray:
        # Grid coordinates
        z, y, x = np.mgrid[0:self.depth, 0:self.height, 0:self.width]
        
        # Physical coordinates (meters)
        x_m = x * (self.resolution / 1000.0)
        y_m = y * (self.resolution / 1000.0)
        z_m = z * (self.resolution / 1000.0)
        
        field = np.zeros((self.depth, self.height, self.width))
        
        for e in emitters:
            # Emitter pos in grid coords
            ex_m = e.x * (self.resolution / 1000.0)
            ey_m = e.y * (self.resolution / 1000.0)
            ez_m = getattr(e, 'z', 0) * (self.resolution / 1000.0) # Support 'z' in Emitter
            
            dist_m = np.sqrt((x_m - ex_m)**2 + (y_m - ey_m)**2 + (z_m - ez_m)**2)
            
            # 40kHz standard
            real_freq = 30000 + (e.frequency * 20000)
            k = 2 * np.pi * real_freq / self.wave_speed
            
            # Simple Pressure field
            field += e.amplitude * np.cos(k * dist_m + e.phase)
            
        return field
