import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# --- EXPERIMENT: SOCIAL LEARNING (The Hive Mind) ---

class Problem:
    """Target: Minimize Sphere Function f(x) = sum(x^2)"""
    @staticmethod
    def evaluate(params):
        return np.sum(params**2)

class Agent:
    def __init__(self, dim=5, learning_type="SOLITARY"): # Reduced Dim
        self.dim = dim
        self.params = np.random.uniform(-5.0, 5.0, dim)
        self.fitness = Problem.evaluate(self.params)
        self.learning_type = learning_type
        self.best_params = np.copy(self.params)
        self.best_fitness = self.fitness

    def learn(self, neighbors=None):
        # Save current state
        old_params = np.copy(self.params)
        old_fitness = self.fitness
        
        # 1. Individual Learning (Mutation / Exploration)
        mutation = np.random.normal(0, 0.5, self.dim) # Increased mutation size
        
        # 2. Social Learning (Exploitation of Peers)
        social_vector = np.zeros(self.dim)
        
        if self.learning_type == "SOCIAL" and neighbors:
            # Find best neighbor
            best_neighbor = min(neighbors, key=lambda x: x.fitness)
            
            if best_neighbor.fitness < self.fitness:
                # Copying / Gravitating towards success
                # Move towards neighbor
                social_vector = (best_neighbor.params - self.params) * 0.8 # Strong pull
        
        # Propose new params
        if self.learning_type == "SOCIAL":
            self.params += social_vector + mutation
        else:
            self.params += mutation
            
        # Boundary check
        self.params = np.clip(self.params, -5.0, 5.0)
        
        # 3. Selection (Hill Climbing)
        # Evaluate new params immediately (Greedy)
        new_fitness = Problem.evaluate(self.params)
        
        if new_fitness < old_fitness:
            # Improvement! Keep it.
            self.fitness = new_fitness
        else:
            # No improvement. Revert.
            # But for Social, maybe we accept some bad moves? 
            # No, let's be strict for this test to prove speedup.
            self.params = old_params
            self.fitness = old_fitness

def run_swarm(learning_type, n_agents=20, max_gens=500, target_fitness=0.1): # Relaxed Target, More Gens
    agents = [Agent(learning_type=learning_type) for _ in range(n_agents)]
    history = []
    
    for gen in range(max_gens):
        # Evaluate
        # Note: In our new logic, evaluation happens inside learn() for selection.
        # But we still need to find global best for reporting.
        
        # Get Global Best
        global_best = min(agents, key=lambda x: x.fitness).fitness
        history.append(global_best)
        
        if gen % 50 == 0:
            print(f"    Gen {gen}: Best Fitness = {global_best:.6f}")
        
        if global_best < target_fitness:
            return gen, history
            
        # Learn
        for i, agent in enumerate(agents):
            # Define neighbors (Ring topology for simplicity)
            left = agents[(i - 1) % n_agents]
            right = agents[(i + 1) % n_agents]
            neighbors = [left, right]
            
            agent.learn(neighbors)
            
    return max_gens, history

def social_learning_test():
    print("\n--- PAPER 18: SOCIAL LEARNING TEST ---")
    
    # Run Solitary Swarm
    print("Running Solitary Swarm (Individual Learning)...")
    gen_solitary, hist_solitary = run_swarm("SOLITARY")
    print(f"  Solitary Convergence: {gen_solitary} generations")
    
    # Run Social Swarm
    print("Running Social Swarm (Hive Mind)...")
    gen_social, hist_social = run_swarm("SOCIAL")
    print(f"  Social Convergence:   {gen_social} generations")
    
    # Comparison
    speedup = gen_solitary / (gen_social + 1e-6)
    print(f"\nSpeedup Factor: {speedup:.2f}x")
    
    if gen_social < gen_solitary:
        print("\nSUCCESS: Social Learning converged faster.")
    else:
        print("\nFAILURE: Social Learning did not outperform Individual Learning.")

if __name__ == "__main__":
    social_learning_test()
