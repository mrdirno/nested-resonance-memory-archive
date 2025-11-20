import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# --- EXPERIMENT: THE OMEGA POINT (Recursive Self-Improvement) ---

class Agent:
    def __init__(self, dim=5, meta_learning=False):
        self.dim = dim
        self.meta_learning = meta_learning
        
        # Primary Parameters (The "Solution")
        self.params = np.random.uniform(-5, 5, dim)
        
        # Hyperparameters (The "Learning Strategy")
        # If meta_learning is True, these evolve. If False, they are fixed.
        self.learning_rate = 0.1
        self.mutation_rate = 0.1
        
        self.fitness = float('inf')
        
    def evaluate(self):
        # Objective: Minimize Sphere Function
        self.fitness = np.sum(self.params**2)
        return self.fitness
        
    def mutate(self):
        # Mutate Primary Parameters
        noise = np.random.normal(0, self.mutation_rate, self.dim)
        self.params += noise
        
        # Mutate Hyperparameters (Meta-Learning)
        if self.meta_learning:
            # Evolve Learning Rate
            if np.random.random() < 0.1:
                self.learning_rate *= np.random.choice([0.8, 1.2])
                self.learning_rate = np.clip(self.learning_rate, 0.001, 1.0)
                
            # Evolve Mutation Rate
            if np.random.random() < 0.1:
                self.mutation_rate *= np.random.choice([0.8, 1.2])
                self.mutation_rate = np.clip(self.mutation_rate, 0.001, 1.0)

def run_simulation(mode, generations=100, pop_size=50):
    meta = (mode == "META")
    population = [Agent(meta_learning=meta) for _ in range(pop_size)]
    
    best_fitness_history = []
    
    for g in range(generations):
        # 1. Evaluate
        for agent in population:
            agent.evaluate()
            
        # Sort by fitness (lower is better)
        population.sort(key=lambda x: x.fitness)
        best_fitness_history.append(population[0].fitness)
        
        # 2. Selection & Reproduction (Elitism + Mutation)
        # Keep top 20%
        survivors = population[:int(pop_size*0.2)]
        
        new_population = []
        while len(new_population) < pop_size:
            parent = np.random.choice(survivors)
            child = Agent(meta_learning=meta)
            
            # Copy Genome
            child.params = parent.params.copy()
            child.learning_rate = parent.learning_rate
            child.mutation_rate = parent.mutation_rate
            
            # Mutate
            child.mutate()
            new_population.append(child)
            
        population = new_population
        
    return best_fitness_history, population[0]

def omega_point_test():
    print("\n--- PAPER 20: THE OMEGA POINT TEST ---")
    
    # Run Fixed Learning
    print("Running Fixed Learning (Static Hyperparams)...")
    hist_fixed, best_fixed = run_simulation("FIXED")
    print(f"  Fixed Final Error: {hist_fixed[-1]:.6f}")
    
    # Run Meta Learning
    print("Running Meta Learning (Evolving Hyperparams)...")
    hist_meta, best_meta = run_simulation("META")
    print(f"  Meta Final Error: {hist_meta[-1]:.6f}")
    print(f"  Meta Final Mutation Rate: {best_meta.mutation_rate:.6f}")
    
    # Comparison
    improvement = hist_fixed[-1] / (hist_meta[-1] + 1e-9)
    print(f"\nSpeedup Factor: {improvement:.2f}x")
    
    if hist_meta[-1] < hist_fixed[-1]:
        print("\nSUCCESS: Meta-Learning outperformed Fixed Learning.")
    else:
        print("\nFAILURE: Meta-Learning did not improve performance.")

if __name__ == "__main__":
    omega_point_test()
