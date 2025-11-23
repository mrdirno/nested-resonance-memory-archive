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
        """
        Calculates the complex pressure field.
        Returns a 3D numpy array of complex values.
        """
        # Grid coordinates
        z, y, x = np.mgrid[0:self.depth, 0:self.height, 0:self.width]
        
        # Physical coordinates (meters)
        x_m = x * (self.resolution / 1000.0)
        y_m = y * (self.resolution / 1000.0)
        z_m = z * (self.resolution / 1000.0)
        
        field = np.zeros((self.depth, self.height, self.width), dtype=complex)
        
        for e in emitters:
            # Emitter pos in mm (Physical coordinates)
            # Convert mm to meters
            ex_m = e.x / 1000.0
            ey_m = e.y / 1000.0
            ez_m = getattr(e, 'z', 0) / 1000.0
            
            dist_m = np.sqrt((x_m - ex_m)**2 + (y_m - ey_m)**2 + (z_m - ez_m)**2)
            
            # Avoid division by zero at emitter location
            dist_m[dist_m == 0] = 1e-9
            
            # 40kHz standard
            real_freq = 30000 + (e.frequency * 20000)
            k = 2 * np.pi * real_freq / self.wave_speed
            
            # Complex Pressure: P = (A/r) * e^(i(kr + phi))
            # We ignore 1/r decay for now to match previous simplified model, 
            # or add it for realism. Let's stick to the previous model's amplitude 
            # but make it complex: A * e^(i(kr + phi))
        field += e.amplitude * np.exp(1j * (k * dist_m + e.phase))
            
        return field

    def propagate_slice(self, emitters: list, z_layer: int) -> np.ndarray:
        """
        Calculates the complex pressure field for a single Z-slice.
        Returns a 2D numpy array of complex values.
        """
        # Grid coordinates for one slice
        y, x = np.mgrid[0:self.height, 0:self.width]
        z = np.full_like(x, z_layer)
        
        # Physical coordinates (meters)
        x_m = x * (self.resolution / 1000.0)
        y_m = y * (self.resolution / 1000.0)
        z_m = z * (self.resolution / 1000.0)
        
        field = np.zeros((self.height, self.width), dtype=complex)
        
        for e in emitters:
            # Emitter pos in mm (Physical coordinates)
            # Convert mm to meters
            ex_m = e.x / 1000.0
            ey_m = e.y / 1000.0
            ez_m = getattr(e, 'z', 0) / 1000.0
            
            dist_m = np.sqrt((x_m - ex_m)**2 + (y_m - ey_m)**2 + (z_m - ez_m)**2)
            
            # Avoid division by zero at emitter location
            dist_m[dist_m == 0] = 1e-9
            
            # 40kHz standard
            real_freq = 30000 + (e.frequency * 20000)
            k = 2 * np.pi * real_freq / self.wave_speed
            
            field += e.amplitude * np.exp(1j * (k * dist_m + e.phase))
            
        return field

    def calculate_gorkov_potential(self, field: np.ndarray) -> np.ndarray:
        """
        Calculates the Gorkov Potential (U) from the complex pressure field.
        U = K1 * |p|^2 - K2 * |grad(p)|^2
        Traps are minima of U.
        """
        # Physical Constants for Air/Styrofoam at 40kHz
        rho_0 = 1.2 # Air density (kg/m^3)
        c_0 = 343.0 # Sound speed (m/s)
        rho_p = 25.0 # Particle density (kg/m^3)
        c_p = 2350.0 # Particle sound speed (m/s)
        R = 0.001 # Particle radius (1mm)
        omega = 2 * np.pi * 40000 # 40kHz
        
        # Coefficients
        # f1 (Monopole) = 1 - rho_0*c_0^2 / (rho_p*c_p^2)
        f1 = 1.0 - (rho_0 * c_0**2) / (rho_p * c_p**2)
        
        # f2 (Dipole) = 2*(rho_p - rho_0) / (2*rho_p + rho_0)
        f2 = 2 * (rho_p - rho_0) / (2 * rho_p + rho_0)
        
        # Pre-factors
        V_p = (4/3) * np.pi * R**3
        K1 = V_p / (4 * rho_0 * c_0**2) * f1
        K2 = (3/4) * V_p / (rho_0 * omega**2) * f2 # Note: 3/4 factor comes from derivation
        
        # Mean Square Pressure <p^2> = 0.5 * |p|^2
        p_sq = 0.5 * np.abs(field)**2
        
        # Mean Square Velocity <v^2> proportional to |grad(p)|^2
        # grad(p)
        # We need gradient in meters, not pixels.
        # np.gradient returns d/dn where n is index. 
        # d/dx_m = (d/dn) * (dn/dx_m) = (d/dn) * (1 / resolution_m)
        res_m = self.resolution / 1000.0
        grad_z, grad_y, grad_x = np.gradient(field, res_m)
        
        grad_sq = 0.5 * (np.abs(grad_x)**2 + np.abs(grad_y)**2 + np.abs(grad_z)**2)
        
        # Gorkov Potential
        # U = 2*pi*R^3 * [ (<p^2> / (3*rho_0*c_0^2)) * f1  - (rho_0*<v^2> / 2) * f2 ]
        # Let's use the simplified K1, K2 form:
        # U = V_p * [ f1 * <p^2> / (rho_0 * c_0^2) - f2 * 3/2 * <v^2> * rho_0 ] ???
        # Let's stick to the standard derived formula:
        # U = 2 * pi * R^3 * [ <p^2>/(3*rho_0*c_0^2) * f1 - rho_0*<v^2>/2 * f2 ]
        
        # Re-calculating terms to match standard formula exactly:
        term1 = (p_sq / (3 * rho_0 * c_0**2)) * f1
        
        # v = -1/(i*omega*rho_0) * grad(p)
        # |v|^2 = 1/(omega^2 * rho_0^2) * |grad(p)|^2
        # <v^2> = 0.5 * |v|^2 = 0.5 / (omega^2 * rho_0^2) * |grad(p)|^2
        
        v_sq = (0.5 / (omega**2 * rho_0**2)) * (np.abs(grad_x)**2 + np.abs(grad_y)**2 + np.abs(grad_z)**2)
        
        term2 = (rho_0 * v_sq / 2) * f2
        
        U = 2 * np.pi * R**3 * (term1 - term2)
        
        return U
