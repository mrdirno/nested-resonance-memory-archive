"""
Cycle 2430: Optimize MPS Solver (Gate 58)
Role: The Optimizer
Responsibility: Speed up the Genetic Algorithm by pre-computing distance matrices and using GEMM.
"""

import time
import torch
import numpy as np
import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios.ga_gpu import GeneticAlgorithmGPU
from nrm_core.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
from nrm_core.helios.types import Emitter3D

class OptimizedGeneticAlgorithmGPU(GeneticAlgorithmGPU):
    def __init__(self, substrate_gpu, emitters):
        super().__init__(substrate_gpu, emitters)
        
        # OPTIMIZATION: Pre-compute Base Components for GEMM
        print("Pre-computing GEMM matrices...")
        
        x_m = self.substrate.x_m
        y_m = self.substrate.y_m
        z_m = self.substrate.z_m
        
        # Calculate base phase k*d
        base_phase = torch.zeros((self.num_emitters, self.substrate.depth,
                                  self.substrate.height, self.substrate.width),
                                 device=self.device, dtype=torch.float32)
                                      
        for i in range(self.num_emitters):
            dist_m = torch.sqrt((x_m - self.emitter_x[i])**2 +
                               (y_m - self.emitter_y[i])**2 +
                               (z_m - self.emitter_z[i])**2)
            dist_m = torch.clamp(dist_m, min=1e-9)
            
            real_freq = 30000 + (self.emitter_freq[i] * 20000)
            k = 2 * np.pi * real_freq / self.substrate.wave_speed
            
            base_phase[i] = k * dist_m
            
        # Flatten spatial dimensions: (num_emitters, V)
        V = self.substrate.depth * self.substrate.height * self.substrate.width
        base_phase_flat = base_phase.view(self.num_emitters, V)
        
        # Precompute terms
        # Term1 = Amp * cos(base)
        # Term2 = Amp * sin(base)
        self.term1 = (self.emitter_amp.view(-1, 1) * torch.cos(base_phase_flat)).contiguous()
        self.term2 = (self.emitter_amp.view(-1, 1) * torch.sin(base_phase_flat)).contiguous()
        
        # Clean up intermediates
        del base_phase
        del base_phase_flat
            
    def propagate_batch(self, phases_batch):
        """
        GEMM-based propagation.
        phases_batch: (pop, num_emitters)
        """
        # cos(A+B) = cosA cosB - sinA sinB
        # sin(A+B) = sinA cosB + cosA sinB
        # Here A = base_phase (Term1/2), B = emitter_phase (phases_batch)
        
        # Prepare B components
        # shape: (pop, num_emitters)
        cos_B = torch.cos(phases_batch)
        sin_B = torch.sin(phases_batch)
        
        # Field Real = Sum [ Amp * cos(A+B) ]
        # = Sum [ Amp * (cosA cosB - sinA sinB) ]
        # = Sum [ (Amp cosA) * cosB - (Amp sinA) * sinB ]
        # = Sum [ Term1 * cosB - Term2 * sinB ]
        # Matrix mult: cos_B @ Term1 - sin_B @ Term2
        
        # (pop, num_emitters) @ (num_emitters, V) -> (pop, V)
        
        field_real = torch.mm(cos_B, self.term1) - torch.mm(sin_B, self.term2)
        field_imag = torch.mm(sin_B, self.term1) + torch.mm(cos_B, self.term2)
        
        # Magnitude Squared
        potential_flat = field_real**2 + field_imag**2
        
        # Reshape to (pop, D, H, W)
        return potential_flat.view(phases_batch.shape[0], 
                                   self.substrate.depth, 
                                   self.substrate.height, 
                                   self.substrate.width)

    def evaluate_fitness_batch(self, phases_batch, target_positions):
        # Re-implementing extraction logic to ensure it works with new propagate
        potentials = self.propagate_batch(phases_batch)
        
        indices_x = []
        indices_y = []
        indices_z = []
        
        for t in target_positions:
            tx = int(t[0] / self.substrate.resolution)
            ty = int(t[1] / self.substrate.resolution)
            tz = int(t[2] / self.substrate.resolution)
            
            if (0 <= tx < potentials.shape[3] and
                0 <= ty < potentials.shape[2] and
                0 <= tz < potentials.shape[1]):
                indices_x.append(tx)
                indices_y.append(ty)
                indices_z.append(tz)
                
        if not indices_x:
            return torch.ones(phases_batch.shape[0], device=self.device) * -500.0
            
        idx_x = torch.tensor(indices_x, device=self.device)
        idx_y = torch.tensor(indices_y, device=self.device)
        idx_z = torch.tensor(indices_z, device=self.device)
        
        target_vals = potentials[:, idx_z, idx_y, idx_x]
        fitness = torch.sum(-target_vals, dim=1)
        
        return fitness

def benchmark():
    print("Benchmarking Solver Optimization (GEMM)...")
    
    # Setup
    emitters = [Emitter3D(x, y, 1.0, 0.0, 1.0, 0.0) for x in range(0, 80, 10) for y in range(0, 80, 10)]
    targets = [np.array([40, 40, 40])]
    
    # Grid: 100mm^3, 2mm res -> 50^3 = 125k voxels
    substrate = AcousticSubstrate3DGPU(100, 100, 100, 2)
    
    # 1. Baseline
    print("\n--- Baseline GeneticAlgorithmGPU ---")
    baseline = GeneticAlgorithmGPU(substrate, emitters)
    start = time.time()
    baseline.solve(targets, generations=20, pop_size=100)
    end = time.time()
    print(f"Baseline Time: {end - start:.4f}s")
    
    # 2. Optimized
    print("\n--- OptimizedGeneticAlgorithmGPU ---")
    optimized = OptimizedGeneticAlgorithmGPU(substrate, emitters)
    start = time.time()
    optimized.solve(targets, generations=20, pop_size=100)
    end = time.time()
    print(f"Optimized Time: {end - start:.4f}s")

if __name__ == "__main__":
    benchmark()