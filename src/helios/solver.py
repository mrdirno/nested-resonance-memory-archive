
"""
Helios: Inverse Physics Solver (Genetic Algorithm)
==================================================
This module implements an evolutionary solver to determine the optimal 
emitter phases required to generate a specific target acoustic field.

Core Logic:
1. Genome: Array of phase delays [phi_1, phi_2, ..., phi_N] for N emitters.
2. Fitness: -MSE between simulated field and target field.
3. Evolution: Tournament selection, crossover, and mutation.

Gate 3.2 Compliant.
"""

import numpy as np
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Import core physics engine
# Assuming nrm_core is in python path or installed
try:
    from nrm_core.helios.substrate import SubstrateInterface
except ImportError:
    # Fallback for development environment without full installation
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from nrm_core.helios.substrate import SubstrateInterface

@dataclass
class SolverConfig:
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    tournament_size: int = 5
    elite_count: int = 2

class InverseSolver:
    def __init__(self, 
                 substrate: SubstrateInterface, 
                 target_field: np.ndarray,
                 config: SolverConfig = SolverConfig()):
        """
        Initialize the Inverse Solver.
        
        Args:
            substrate: The physics engine instance (defines emitters and field logic).
            target_field: 2D/3D numpy array representing desired pressure/potential.
            config: Genetic Algorithm hyperparameters.
        """
        self.substrate = substrate
        self.target_field = target_field
        self.config = config
        
        # Emitter count determines genome size
        # (Assuming substrate has an 'emitters' list or similar property)
        # If substrate is abstract, we might need to pass emitter count explicitly
        # For now, let's assume substrate.num_emitters exists or len(substrate.emitters)
        try:
            self.genome_size = len(substrate.emitters)
        except AttributeError:
            # Fallback or error if substrate not initialized
            self.genome_size = 64 # Default for testing
            
        self.population = self._initialize_population()
        self.history = []

    def _initialize_population(self) -> np.ndarray:
        """Create random initial population of phases [0, 2pi]."""
        return np.random.uniform(0, 2 * np.pi, (self.config.population_size, self.genome_size))

    def _calculate_fitness(self, genome: np.ndarray) -> float:
        """
        Evaluate a single genome.
        Fitness = -MSE (Mean Squared Error) between generated and target field.
        """
        # 1. Configure substrate with genome phases
        self.substrate.set_phases(genome)
        
        # 2. Simulate field
        # Assuming substrate.simulate() returns the field array matching target shape
        generated_field = self.substrate.simulate()
        
        # 3. Calculate Error
        # We might care about shape (correlation) or absolute value (MSE)
        # For levitation, we usually want Gorkov potential minima at specific points
        # If target_field is a boolean mask of "trap here", we check values at those indices
        
        # Simple MSE for now:
        # Normalize both to 0-1 for fair comparison if needed, but raw might be better for potential
        mse = np.mean((generated_field - self.target_field) ** 2)
        
        return -mse # Maximize this

    def solve(self) -> Tuple[np.ndarray, float]:
        """
        Execute the evolutionary loop.
        Returns: (best_phases, best_fitness)
        """
        print(f"Starting Inverse Solver (Pop: {self.config.population_size}, Gens: {self.config.generations})")
        
        start_time = time.time()
        
        for generation in range(self.config.generations):
            fitness_scores = np.array([self._calculate_fitness(ind) for ind in self.population])
            
            # Record stats
            best_idx = np.argmax(fitness_scores)
            best_fitness = fitness_scores[best_idx]
            avg_fitness = np.mean(fitness_scores)
            self.history.append((best_fitness, avg_fitness))
            
            # Logging
            if generation % 10 == 0:
                print(f"Gen {generation}: Best Fitness = {best_fitness:.6f}")
                
            # Elitism
            sorted_indices = np.argsort(fitness_scores)[::-1]
            new_population = [self.population[i] for i in sorted_indices[:self.config.elite_count]]
            
            # Selection & Crossover & Mutation
            while len(new_population) < self.config.population_size:
                # Tournament Selection
                parent1 = self._tournament_select(fitness_scores)
                parent2 = self._tournament_select(fitness_scores)
                
                # Crossover
                if np.random.random() < self.config.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                    
                # Mutation
                child = self._mutate(child)
                new_population.append(child)
                
            self.population = np.array(new_population)
            
        # Final result
        total_time = time.time() - start_time
        fitness_scores = np.array([self._calculate_fitness(ind) for ind in self.population])
        best_idx = np.argmax(fitness_scores)
        
        print(f"Solver Complete. Time: {total_time:.2f}s. Best Fitness: {fitness_scores[best_idx]:.6f}")
        
        return self.population[best_idx], fitness_scores[best_idx]

    def _tournament_select(self, fitness_scores: np.ndarray) -> np.ndarray:
        """Select best individual from random subset."""
        indices = np.random.randint(0, self.config.population_size, self.config.tournament_size)
        tournament_fitness = fitness_scores[indices]
        winner_idx = indices[np.argmax(tournament_fitness)]
        return self.population[winner_idx]

    def _crossover(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
        """Uniform Crossover."""
        mask = np.random.rand(self.genome_size) > 0.5
        child = np.where(mask, p1, p2)
        return child

    def _mutate(self, genome: np.ndarray) -> np.ndarray:
        """Gaussian Mutation."""
        if np.random.random() < self.config.mutation_rate:
            mutation = np.random.normal(0, 0.5, self.genome_size) # Std dev 0.5 radians
            genome += mutation
            # Wrap phases to [0, 2pi]
            genome = np.mod(genome, 2 * np.pi)
        return genome
