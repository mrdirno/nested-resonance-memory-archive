"""
HELIOS Waveform Solver (Gate 3.2)
Inverse Physics Engine: Calculates emitter parameters (Phase/Frequency) to match a Target Density Field.

Principle: PRIN-INVERSE-DESIGN
Author: MOG (Cycle 2342)
"""

import numpy as np
import time
import torch
try:
    from nrm_core.helios.ga_gpu import GeneticAlgorithmGPU
    from nrm_core.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
    from nrm_core.helios.types import Emitter3D
    HAS_CORE = True
except ImportError as e:
    print(f"Core Import Error: {e}")
    HAS_CORE = False

class InverseSolver:
    def __init__(self, target_field, emitters, physics_config, resolution=2.0):
        """
        Initialize the Inverse Solver.
        :param target_field: 3D numpy array (N x N x N) representing desired density.
        :param emitters: List of [x, y, z] lists.
        :param physics_config: Dictionary of physics constants (c, rho, etc).
        :param resolution: Grid resolution in mm.
        """
        self.target = target_field
        self.raw_emitters = emitters
        self.config = physics_config
        self.resolution = resolution
        self.population_size = 100
        self.mutation_rate = 0.1
        self.generations = 50
        
        # Initialize Substrate if Core is available
        self.substrate = None
        self.ga = None
        
        if HAS_CORE:
            D, H, W = target_field.shape
            # Create Substrate matching target dimensions
            # Resolution is passed in mm
            self.substrate = AcousticSubstrate3DGPU(
                width_mm=W*resolution,
                height_mm=H*resolution,
                depth_mm=D*resolution,
                resolution_mm=resolution
            )
            
            # Convert raw emitters to Emitter3D objects
            scale_x = W * resolution
            scale_y = H * resolution
            
            self.core_emitters = []
            for i, e in enumerate(emitters):
                # e is [x, y, z] normalized 0..1
                ex = e[0] * scale_x
                ey = e[1] * scale_y
                ez = e[2] * scale_x # Assume cubic workspace for z scaling
                
                self.core_emitters.append(Emitter3D(ex, ey, 1.0, 0.0, 1.0, ez))
                
            self.ga = GeneticAlgorithmGPU(self.substrate, self.core_emitters)

    def evolve(self):
        """
        Run Genetic Algorithm to find optimal phases.
        """
        if not self.ga:
            print("Fallback: Returning random phases (Core not available)")
            return np.random.uniform(0, 2*np.pi, len(self.raw_emitters))
            
        print(f"Starting GPU Evolution: {len(self.raw_emitters)} emitters, {self.generations} generations.")
        start_time = time.time()
        
        # Convert target field (voxels) to target points (mm)
        # indices are (z, y, x)
        indices = np.argwhere(self.target > 0.5)
        
        target_points = []
        for idx in indices:
            z, y, x = idx
            # Convert to mm
            px = x * self.resolution
            py = y * self.resolution
            pz = z * self.resolution
            target_points.append(np.array([px, py, pz]))
            
        if not target_points:
            print("Warning: No target points found in field.")
            return np.zeros(len(self.raw_emitters))

        # Run GA
        best_phases = self.ga.solve(target_points, generations=self.generations, pop_size=self.population_size)
        
        print(f"Solved in {time.time() - start_time:.2f}s.")
        return best_phases

    def get_field(self, phases):
        """
        Calculate the volumetric pressure field for the given phases.
        Returns: 3D numpy array (Potential)
        """
        if not self.ga:
            return np.zeros_like(self.target)
            
        # Convert phases to tensor (1, num_emitters)
        phases_tensor = torch.tensor(phases, device=self.ga.device, dtype=torch.float32).unsqueeze(0)
        
        # Propagate
        with torch.no_grad():
            potential = self.ga.propagate_batch(phases_tensor) # (1, D, H, W)
            
        return potential[0].cpu().numpy()

if __name__ == "__main__":
    # Self-test
    target_dummy = np.zeros((32, 32, 32))
    target_dummy[16, 16, 16] = 1.0 # Single point
    
    emitters_dummy = [ [0.5, 0.5, 0.0] for _ in range(64) ] # 64 emitters
    config_dummy = {"c": 343, "rho": 1.2}
    
    solver = InverseSolver(target_dummy, emitters_dummy, config_dummy)
    solution = solver.evolve()
    print(f"Solution shape: {solution.shape}")
    
    field = solver.get_field(solution)
    print(f"Field shape: {field.shape}")
    print(f"Max potential: {field.max()}")
# [SPORE] ID: The Colony
