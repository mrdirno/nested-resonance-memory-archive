"""
HELIOS 3D Substrate Interface - GPU Accelerated (MPS/CUDA)
Extension of the Substrate architecture for Volumetric compilation.

Cycle 367: GPU Acceleration for acoustic field propagation.
Uses PyTorch with MPS (Apple Silicon) or CUDA (NVIDIA) backends.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
from abc import ABC, abstractmethod
import numpy as np
import torch

class SubstrateInterface3DGPU(ABC):
    """
    Abstract Base Class for GPU-accelerated 3D physical substrates.
    """

    def __init__(self, width: int, height: int, depth: int, wave_speed: float, damping: float):
        self.width = width
        self.height = height
        self.depth = depth
        self.wave_speed = wave_speed
        self.damping = damping

        # Auto-detect best device
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

    @abstractmethod
    def propagate(self, emitters: list) -> np.ndarray:
        """
        Calculates the field in 3D space (x, y, z).
        Returns a 3D numpy array.
        """
        pass

class AcousticSubstrate3DGPU(SubstrateInterface3DGPU):
    """
    GPU-Accelerated 3D Acoustic Simulator using PyTorch.
    """
    def __init__(self, width_mm=50, height_mm=50, depth_mm=50, resolution_mm=1):
        w_pixels = int(width_mm / resolution_mm)
        h_pixels = int(height_mm / resolution_mm)
        d_pixels = int(depth_mm / resolution_mm)
        super().__init__(w_pixels, h_pixels, d_pixels, wave_speed=343.0, damping=0.001)
        self.resolution = resolution_mm

        # Pre-compute grid coordinates on GPU (reusable across propagate calls)
        z_idx = torch.arange(self.depth, device=self.device, dtype=torch.float32)
        y_idx = torch.arange(self.height, device=self.device, dtype=torch.float32)
        x_idx = torch.arange(self.width, device=self.device, dtype=torch.float32)

        # Create meshgrid [depth, height, width]
        self.z_grid, self.y_grid, self.x_grid = torch.meshgrid(z_idx, y_idx, x_idx, indexing='ij')

        # Convert to meters
        self.x_m = self.x_grid * (self.resolution / 1000.0)
        self.y_m = self.y_grid * (self.resolution / 1000.0)
        self.z_m = self.z_grid * (self.resolution / 1000.0)

    def propagate(self, emitters: list) -> np.ndarray:
        """
        GPU-accelerated calculation of the complex pressure field.
        Returns a 3D numpy array of complex values.
        """
        # Initialize field on GPU
        field_real = torch.zeros((self.depth, self.height, self.width),
                                 device=self.device, dtype=torch.float32)
        field_imag = torch.zeros((self.depth, self.height, self.width),
                                 device=self.device, dtype=torch.float32)

        for e in emitters:
            # Emitter position in meters
            ex_m = e.x / 1000.0
            ey_m = e.y / 1000.0
            ez_m = getattr(e, 'z', 0) / 1000.0

            # Distance calculation (fully on GPU)
            dist_m = torch.sqrt((self.x_m - ex_m)**2 +
                               (self.y_m - ey_m)**2 +
                               (self.z_m - ez_m)**2)

            # Avoid division by zero
            dist_m = torch.clamp(dist_m, min=1e-9)

            # Wave number
            real_freq = 30000 + (e.frequency * 20000)
            k = 2 * np.pi * real_freq / self.wave_speed

            # Phase term
            phase = k * dist_m + e.phase

            # Add contribution (complex exponential)
            field_real += e.amplitude * torch.cos(phase)
            field_imag += e.amplitude * torch.sin(phase)

        # Combine to complex numpy array
        result_real = field_real.cpu().numpy()
        result_imag = field_imag.cpu().numpy()

        return result_real + 1j * result_imag

    def calculate_gorkov_potential(self, field: np.ndarray) -> np.ndarray:
        """
        GPU-accelerated Gorkov Potential calculation.
        U = acoustic radiation force potential.
        Traps are minima of U.
        """
        # Convert to torch tensors on GPU
        field_real = torch.tensor(field.real, device=self.device, dtype=torch.float32)
        field_imag = torch.tensor(field.imag, device=self.device, dtype=torch.float32)

        # Physical Constants for Air/Styrofoam at 40kHz
        rho_0 = 1.2  # Air density (kg/m^3)
        c_0 = 343.0  # Sound speed (m/s)
        rho_p = 25.0  # Particle density (kg/m^3)
        c_p = 2350.0  # Particle sound speed (m/s)
        R = 0.001  # Particle radius (1mm)
        omega = 2 * np.pi * 40000  # 40kHz

        # Coefficients
        f1 = 1.0 - (rho_0 * c_0**2) / (rho_p * c_p**2)
        f2 = 2 * (rho_p - rho_0) / (2 * rho_p + rho_0)

        # Mean Square Pressure <p^2> = 0.5 * |p|^2
        p_sq = 0.5 * (field_real**2 + field_imag**2)

        # Gradient calculation on GPU
        res_m = self.resolution / 1000.0

        # PyTorch gradient (diff along each dimension)
        # For 3D: dim 0 = z, dim 1 = y, dim 2 = x
        def torch_gradient(f, spacing):
            # Simple central difference approximation
            grad = []
            for dim in range(3):
                padded = torch.nn.functional.pad(f.unsqueeze(0).unsqueeze(0),
                    [1 if i == 2-dim else 0 for i in range(6)],
                    mode='replicate').squeeze()

                # Forward difference
                if dim == 0:  # z
                    g = (f[1:, :, :] - f[:-1, :, :]) / spacing
                    g = torch.nn.functional.pad(g.unsqueeze(0).unsqueeze(0),
                        (0, 0, 0, 0, 0, 1), mode='replicate').squeeze()
                elif dim == 1:  # y
                    g = (f[:, 1:, :] - f[:, :-1, :]) / spacing
                    g = torch.nn.functional.pad(g.unsqueeze(0).unsqueeze(0),
                        (0, 0, 0, 1, 0, 0), mode='replicate').squeeze()
                else:  # x
                    g = (f[:, :, 1:] - f[:, :, :-1]) / spacing
                    g = torch.nn.functional.pad(g.unsqueeze(0).unsqueeze(0),
                        (0, 1, 0, 0, 0, 0), mode='replicate').squeeze()
                grad.append(g)
            return grad

        grad_z_r, grad_y_r, grad_x_r = torch_gradient(field_real, res_m)
        grad_z_i, grad_y_i, grad_x_i = torch_gradient(field_imag, res_m)

        # |grad(p)|^2 for complex field
        grad_sq = (grad_x_r**2 + grad_x_i**2 +
                   grad_y_r**2 + grad_y_i**2 +
                   grad_z_r**2 + grad_z_i**2)

        # Velocity squared term
        v_sq = (0.5 / (omega**2 * rho_0**2)) * grad_sq

        # Gorkov potential terms
        term1 = (p_sq / (3 * rho_0 * c_0**2)) * f1
        term2 = (rho_0 * v_sq / 2) * f2

        U = 2 * np.pi * R**3 * (term1 - term2)

        return U.cpu().numpy()


# Benchmark utility
def benchmark_gpu_vs_cpu():
    """
    Compare GPU and CPU performance for field propagation.
    """
    import time
    from substrate_3d import AcousticSubstrate3D

    # Simple emitter class for testing
    class Emitter:
        def __init__(self, x, y, z, amp, freq, phase):
            self.x = x
            self.y = y
            self.z = z
            self.amplitude = amp
            self.frequency = freq
            self.phase = phase

    # Test configuration
    emitters = [Emitter(25, 25, i*5, 1.0, 0.5, i*0.1) for i in range(10)]

    # CPU version
    cpu_substrate = AcousticSubstrate3D(100, 100, 100, 1)
    start = time.time()
    for _ in range(5):
        field_cpu = cpu_substrate.propagate(emitters)
    cpu_time = (time.time() - start) / 5

    # GPU version
    gpu_substrate = AcousticSubstrate3DGPU(100, 100, 100, 1)

    # Warm-up
    _ = gpu_substrate.propagate(emitters)

    start = time.time()
    for _ in range(5):
        field_gpu = gpu_substrate.propagate(emitters)
    gpu_time = (time.time() - start) / 5

    print(f"Substrate size: 100x100x100 (1M voxels)")
    print(f"Emitters: 10")
    print(f"Device: {gpu_substrate.device}")
    print(f"CPU time: {cpu_time*1000:.2f} ms")
    print(f"GPU time: {gpu_time*1000:.2f} ms")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    # Verify correctness
    diff = np.abs(field_cpu - field_gpu).max()
    print(f"Max difference: {diff:.6f}")

    return cpu_time, gpu_time


if __name__ == "__main__":
    print("HELIOS GPU Substrate Benchmark")
    print("=" * 40)
    benchmark_gpu_vs_cpu()
