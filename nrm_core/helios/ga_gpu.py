"""
HELIOS GPU-Accelerated Genetic Algorithm Phase Solver

Cycle 368: GPU acceleration for phase optimization.
Evaluates entire population in parallel on GPU for massive speedup.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import numpy as np
import torch
import random

class GeneticAlgorithmGPU:
    """
    GPU-accelerated Genetic Algorithm for phase optimization.
    Evaluates entire population in parallel for 10-100x speedup.
    """

    def __init__(self, substrate_gpu, emitters):
        """
        Args:
            substrate_gpu: AcousticSubstrate3DGPU instance
            emitters: List of Emitter3D objects
        """
        self.substrate = substrate_gpu
        self.emitters = emitters
        self.num_emitters = len(emitters)
        self.device = substrate_gpu.device

        # Pre-compute emitter positions on GPU
        self.emitter_x = torch.tensor([e.x / 1000.0 for e in emitters],
                                       device=self.device, dtype=torch.float32)
        self.emitter_y = torch.tensor([e.y / 1000.0 for e in emitters],
                                       device=self.device, dtype=torch.float32)
        self.emitter_z = torch.tensor([getattr(e, 'z', 0) / 1000.0 for e in emitters],
                                       device=self.device, dtype=torch.float32)
        self.emitter_amp = torch.tensor([e.amplitude for e in emitters],
                                         device=self.device, dtype=torch.float32)
        self.emitter_freq = torch.tensor([e.frequency for e in emitters],
                                          device=self.device, dtype=torch.float32)

    def propagate_batch(self, phases_batch):
        """
        Propagate field for entire population at once.

        Args:
            phases_batch: Tensor of shape (pop_size, num_emitters)

        Returns:
            fields: Tensor of shape (pop_size, depth, height, width) - complex magnitude
        """
        pop_size = phases_batch.shape[0]

        # Get grid from substrate
        x_m = self.substrate.x_m  # (depth, height, width)
        y_m = self.substrate.y_m
        z_m = self.substrate.z_m

        # Initialize batch fields
        field_real = torch.zeros((pop_size, self.substrate.depth,
                                  self.substrate.height, self.substrate.width),
                                 device=self.device, dtype=torch.float32)
        field_imag = torch.zeros_like(field_real)

        for i in range(self.num_emitters):
            # Distance for this emitter (same for all individuals)
            dist_m = torch.sqrt((x_m - self.emitter_x[i])**2 +
                               (y_m - self.emitter_y[i])**2 +
                               (z_m - self.emitter_z[i])**2)
            dist_m = torch.clamp(dist_m, min=1e-9)

            # Wave number
            real_freq = 30000 + (self.emitter_freq[i] * 20000)
            k = 2 * np.pi * real_freq / self.substrate.wave_speed

            # Phases for this emitter across population: (pop_size,)
            emitter_phases = phases_batch[:, i]

            # Phase term: k*dist + phase
            # k*dist is (depth, height, width)
            # emitter_phases is (pop_size,)
            # Result should be (pop_size, depth, height, width)
            phase_base = k * dist_m  # (D, H, W)
            phase_total = phase_base.unsqueeze(0) + emitter_phases.view(-1, 1, 1, 1)

            # Add contribution
            field_real += self.emitter_amp[i] * torch.cos(phase_total)
            field_imag += self.emitter_amp[i] * torch.sin(phase_total)

        # Return magnitude squared (potential)
        potential = field_real**2 + field_imag**2
        return potential

    def evaluate_fitness_batch(self, phases_batch, target_positions):
        """
        Evaluate fitness for entire population.

        Args:
            phases_batch: Tensor (pop_size, num_emitters)
            target_positions: List of target points (mm)

        Returns:
            fitness: Tensor (pop_size,)
        """
        # Propagate all individuals
        potentials = self.propagate_batch(phases_batch)  # (pop, D, H, W)

        # Get max potential per individual
        p_max = potentials.view(potentials.shape[0], -1).max(dim=1)[0]  # (pop,)

        # Calculate fitness
        fitness = torch.zeros(phases_batch.shape[0], device=self.device)

        for t in target_positions:
            tx = int(t[0] / self.substrate.resolution)
            ty = int(t[1] / self.substrate.resolution)
            tz = int(t[2] / self.substrate.resolution)

            if (0 <= tx < potentials.shape[3] and
                0 <= ty < potentials.shape[2] and
                0 <= tz < potentials.shape[1]):
                p_val = potentials[:, tz, ty, tx]  # (pop,)
                # Want low potential at target (deep well)
                fitness += (p_max - p_val)
            else:
                fitness -= 50.0

        return fitness

    def solve(self, target_positions, generations=50, pop_size=40):
        """
        Run GA optimization.

        Args:
            target_positions: List of numpy arrays (target points in mm)
            generations: Number of GA generations
            pop_size: Population size

        Returns:
            best_phases: numpy array of optimal phases
        """
        # Initialize population on GPU
        population = torch.rand((pop_size, self.num_emitters),
                                device=self.device) * 2 * np.pi

        best_genes = None
        best_score = -9999.0

        for gen in range(generations):
            # Evaluate entire population at once
            fitness = self.evaluate_fitness_batch(population, target_positions)

            # Find best
            max_idx = fitness.argmax()
            if fitness[max_idx].item() > best_score:
                best_score = fitness[max_idx].item()
                best_genes = population[max_idx].clone()

            # Sort by fitness
            sorted_idx = fitness.argsort(descending=True)

            # Elite selection (top 25%)
            elite_count = max(2, pop_size // 4)
            elite_idx = sorted_idx[:elite_count]
            elite = population[elite_idx]

            # Create new population
            new_pop = [elite]

            while sum(p.shape[0] for p in new_pop) < pop_size:
                # Random parents from elite
                p1_idx = random.randint(0, elite_count - 1)
                p2_idx = random.randint(0, elite_count - 1)
                p1 = elite[p1_idx]
                p2 = elite[p2_idx]

                # Crossover
                cut = random.randint(1, self.num_emitters - 1)
                child = torch.cat([p1[:cut], p2[cut:]])

                # Mutation
                if random.random() < 0.2:
                    mut_idx = random.randint(0, self.num_emitters - 1)
                    child[mut_idx] = random.uniform(0, 2 * np.pi)

                new_pop.append(child.unsqueeze(0))

            population = torch.cat(new_pop, dim=0)[:pop_size]

        return best_genes.cpu().numpy()


def genetic_algorithm_gpu(target_positions, substrate_gpu, emitters,
                          generations=50, pop_size=40):
    """
    Convenience function matching CPU API.
    """
    ga = GeneticAlgorithmGPU(substrate_gpu, emitters)
    return ga.solve(target_positions, generations, pop_size)


# Benchmark
def benchmark_ga():
    """Compare GPU vs CPU GA performance."""
    import time
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    from src.helios.substrate_3d import AcousticSubstrate3D
    from src.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
    from experiments.cycle348_volumetric_printing import (
        genetic_algorithm_multi_target, create_phased_array_6_sides, Emitter3D
    )

    # Setup
    box_dim = 100.0
    emitters = create_phased_array_6_sides(box_dim=box_dim, num_emitters_per_side=8)

    # Target: 8 corners of cube
    offset = 25.0
    targets = [
        np.array([offset, offset, offset]),
        np.array([box_dim - offset, offset, offset]),
        np.array([offset, box_dim - offset, offset]),
        np.array([offset, offset, box_dim - offset]),
        np.array([box_dim - offset, box_dim - offset, offset]),
        np.array([box_dim - offset, offset, box_dim - offset]),
        np.array([offset, box_dim - offset, box_dim - offset]),
        np.array([box_dim - offset, box_dim - offset, box_dim - offset])
    ]

    # CPU benchmark
    box_cpu = AcousticSubstrate3D(width_mm=box_dim, height_mm=box_dim,
                                  depth_mm=box_dim, resolution_mm=2)
    start = time.time()
    cpu_phases = genetic_algorithm_multi_target(targets, box_cpu, emitters,
                                                generations=20, pop_size=20)
    cpu_time = time.time() - start

    # GPU benchmark
    box_gpu = AcousticSubstrate3DGPU(width_mm=box_dim, height_mm=box_dim,
                                     depth_mm=box_dim, resolution_mm=2)

    # Warm-up
    ga = GeneticAlgorithmGPU(box_gpu, emitters)
    _ = ga.solve(targets, generations=5, pop_size=10)

    start = time.time()
    gpu_phases = ga.solve(targets, generations=20, pop_size=20)
    gpu_time = time.time() - start

    print("HELIOS GPU Genetic Algorithm Benchmark")
    print("=" * 45)
    print(f"Emitters: {len(emitters)}")
    print(f"Targets: {len(targets)}")
    print(f"Generations: 20, Population: 20")
    print(f"Device: {box_gpu.device}")
    print(f"\nCPU time: {cpu_time:.2f} s")
    print(f"GPU time: {gpu_time:.2f} s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return cpu_time, gpu_time


if __name__ == "__main__":
    benchmark_ga()
