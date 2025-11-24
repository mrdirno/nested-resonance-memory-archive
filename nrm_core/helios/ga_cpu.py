"""
HELIOS CPU Genetic Algorithm (Reference Implementation)
Standard implementation for benchmarking against GPU.
"""
import numpy as np
import random
from .substrate_3d import AcousticSubstrate3D

def genetic_algorithm_multi_target(targets, substrate: AcousticSubstrate3D, emitters, generations=20, pop_size=20):
    """
    Optimizes phases to minimize pressure at target points (create nodes).
    Returns list of best phases (one per emitter).
    """
    num_emitters = len(emitters)
    
    # Init Population (Random phases)
    population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
    
    best_fitness = -float('inf')
    best_gene = None
    
    for gen in range(generations):
        scores = []
        for gene in population:
            # 1. Apply phases
            for i, e in enumerate(emitters):
                e.phase = gene[i]
                
            # 2. Propagate
            # This is the slow part on CPU
            field = substrate.propagate(emitters)
            
            # 3. Evaluate (Potential at targets)
            U = substrate.calculate_gorkov_potential(field)
            
            total_u = 0.0
            valid_points = 0
            
            for t in targets:
                # Convert mm to grid index
                tx = int(t[0] / substrate.resolution)
                ty = int(t[1] / substrate.resolution)
                tz = int(t[2] / substrate.resolution)
                
                if 0 <= tx < U.shape[2] and 0 <= ty < U.shape[1] and 0 <= tz < U.shape[0]:
                    val = U[tz, ty, tx]
                    # We want MINIMUM potential (trap)
                    # Fitness = -U (higher is better)
                    total_u -= val # potential is usually negative for trap? 
                    # Wait, Gorkov U is minimized. So Fitness = -U is correct if we want to maximize fitness.
                    # Actually, U can be positive or negative. Stable trap is local minimum.
                    # Let's assume we want to minimize U.
                    # Fitness = -U.
                    # But wait, U values are small.
                    valid_points += 1
                else:
                    total_u -= 100.0 # Penalty for OOB
                    
            if valid_points > 0:
                fitness = total_u / valid_points
            else:
                fitness = -1000.0
                
            scores.append(fitness)
            
            if fitness > best_fitness:
                best_fitness = fitness
                best_gene = gene
                
        # Selection / Evolution
        # Sort
        sorted_indices = np.argsort(scores)[::-1] # Descending
        elite_count = max(2, pop_size // 4)
        elites = [population[i] for i in sorted_indices[:elite_count]]
        
        new_pop = elites[:]
        
        while len(new_pop) < pop_size:
            p1 = random.choice(elites)
            p2 = random.choice(elites)
            
            # Crossover
            cut = random.randint(1, num_emitters-1)
            child = np.concatenate((p1[:cut], p2[cut:]))
            
            # Mutation
            if random.random() < 0.2:
                idx = random.randint(0, num_emitters-1)
                child[idx] = random.uniform(0, 2*np.pi)
                
            new_pop.append(child)
            
        population = new_pop
        
    return best_gene
