
"""
Cycle 2299: Multiverse Optimization
Goal: Use Quantum Branching to explore parameter space and converge on the optimal solution.
Phase 43: The Void (Preparation)

Hypothesis: Parallel exploration of parameters via branching followed by selection is O(1) in subjective time (simulated).
"""

import sys
import os
import numpy as np
import json
import copy

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from experiments.cycle2293_timeline_convergence import ConvergingMultiverse
from experiments.cycle2287_quantum_superposition import QuantumFractalAgent

class OptimizationMultiverse(ConvergingMultiverse):
    def optimize_parameter(self, param_name: str, range_start: float, range_end: float, steps: int):
        """
        Fork universes to cover the parameter range.
        """
        print(f"\n--- Forking {steps} Universes for {param_name} Optimization ---")
        values = np.linspace(range_start, range_end, steps)
        
        # Universe 0 is already there
        self.universes[0]["parameters"] = {param_name: values[0]}
        self.universes[0]["history"].append(f"Set {param_name}={values[0]}")
        
        for i in range(1, steps):
            new_id = self.fork(0)
            self.universes[new_id]["parameters"] = {param_name: values[i]}
            self.universes[new_id]["history"].append(f"Set {param_name}={values[i]}")
            
        return values

    def evaluate_fitness(self, fitness_function):
        """
        Run fitness function in all universes.
        Store result in metadata.
        """
        print("\n--- Evaluating Fitness Across Multiverse ---")
        results = {}
        for uid, state in self.universes.items():
            params = state.get("parameters", {})
            fitness = fitness_function(params)
            state["fitness"] = fitness
            results[uid] = fitness
            print(f"  Universe {uid}: Params={params} -> Fitness={fitness:.4f}")
        return results

    def collapse_to_optimal(self):
        """
        Collapse the multiverse to the single universe with highest fitness.
        """
        print("\n--- Collapsing to Optimal Timeline ---")
        best_uid = -1
        max_fitness = -float('inf')
        
        for uid, state in self.universes.items():
            if state.get("fitness", -float('inf')) > max_fitness:
                max_fitness = state["fitness"]
                best_uid = uid
                
        if best_uid != -1:
            print(f"  > Optimal Timeline Found: Universe {best_uid} (Fitness {max_fitness:.4f})")
            # Prune others
            self.universes = {best_uid: self.universes[best_uid]}
            return best_uid, max_fitness
        return -1, 0.0

# Define a mock complex fitness landscape (Simulation of NRM stability)
# E_consume vs Survival Rate
# Assume inverted U-shape: too low = stagnation, too high = starvation
def nrm_fitness_landscape(params):
    e = params.get("E_consume", 0.5)
    # Optimal around 0.35
    fitness = np.exp(-((e - 0.35)**2) / 0.02)
    # Add some quantum noise
    noise = np.random.normal(0, 0.01)
    return float(np.clip(fitness + noise, 0, 1))

def run_experiment():
    print("Initializing Cycle 2299: Multiverse Optimization...")
    
    mv = OptimizationMultiverse()
    
    # 1. Setup Base
    agent = QuantumFractalAgent("Explorer")
    mv.add_agent(0, agent)
    
    # 2. Fork and Explore
    # Optimizing E_consume from 0.1 to 0.9 in 8 steps
    param_values = mv.optimize_parameter("E_consume", 0.1, 0.9, 8)
    
    # 3. Evaluate
    results = mv.evaluate_fitness(nrm_fitness_landscape)
    
    # 4. Select
    best_uid, best_fitness = mv.collapse_to_optimal()
    
    best_params = mv.universes[best_uid]["parameters"]
    print(f"\nResult: Optimal E_consume = {best_params['E_consume']:.4f}")
    
    # Validation
    expected_optimal = 0.35
    error = abs(best_params['E_consume'] - expected_optimal)
    success = error < 0.15 # Rough check given 8 steps
    
    status = "SUCCESS" if success else "FAILURE"
    print(f"Status: {status}")
    
    # Save
    output_path = "experiments/results/cycle2299_multiverse_optimization.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2299,
            "best_uid": best_uid,
            "best_fitness": best_fitness,
            "best_params": best_params,
            "all_results": results,
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
