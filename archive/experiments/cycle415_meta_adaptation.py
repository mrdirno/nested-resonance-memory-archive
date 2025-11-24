"""
Cycle 415: The Learning Loop (Meta-Adaptation)
Role: The Teacher
Responsibility: Adjust the learning strategy (Mutation Rate) based on student performance (Fitness History).
"""
import random
import numpy as np
import time

class MetaController:
    def __init__(self, initial_mutation_rate=0.1):
        self.base_mutation_rate = initial_mutation_rate
        self.current_mutation_rate = initial_mutation_rate
        self.fitness_history = []
        self.history_window = 5
        self.stagnation_threshold = 0.01
        self.patience = 3
        self.stagnation_counter = 0
        self.mode = "EXPLOIT" # or "EXPLORE"

    def observe(self, current_fitness):
        self.fitness_history.append(current_fitness)
        if len(self.fitness_history) > self.history_window:
            self.fitness_history.pop(0)
        
        return self._decide()

    def _decide(self):
        if len(self.fitness_history) < 2:
            return self.current_mutation_rate

        # Calculate improvement
        recent_improvement = self.fitness_history[-1] - self.fitness_history[0]
        
        # Logic: If stagnant, boost mutation. If improving, cool down.
        if abs(recent_improvement) < self.stagnation_threshold:
            self.stagnation_counter += 1
        else:
            self.stagnation_counter = 0
            
        if self.stagnation_counter >= self.patience:
            # Switch to Exploration
            self.mode = "EXPLORE"
            self.current_mutation_rate = min(0.8, self.current_mutation_rate * 1.5)
        else:
            # Switch to Exploitation (Cooling)
            self.mode = "EXPLOIT"
            self.current_mutation_rate = max(self.base_mutation_rate, self.current_mutation_rate * 0.9)
            
        return self.current_mutation_rate

def run_experiment():
    print("Cycle 415: Meta-Adaptation Test")
    print("===============================")
    
    meta = MetaController(initial_mutation_rate=0.1)
    
    # Simulate a learning process
    # Phase 1: Rapid Improvement (Easy)
    print("\n--- Phase 1: Rapid Improvement ---")
    fitness = 0.0
    for i in range(5):
        fitness += 0.1 # Improving
        mr = meta.observe(fitness)
        print(f"Gen {i}: Fitness {fitness:.2f} | MR: {mr:.3f} | Mode: {meta.mode}")
        
    if meta.mode == "EXPLOIT" and mr <= 0.1:
        print("SUCCESS: System maintained low mutation during improvement.")
    else:
        print("FAIL: System failed to exploit.")

    # Phase 2: Stagnation (Hard Limit)
    print("\n--- Phase 2: Stagnation ---")
    fitness = 0.5 # Stuck
    for i in range(6):
        mr = meta.observe(fitness)
        print(f"Gen {i+5}: Fitness {fitness:.2f} | MR: {mr:.3f} | Mode: {meta.mode}")
        
    if meta.mode == "EXPLORE" and mr > 0.1:
        print("SUCCESS: System detected stagnation and boosted mutation.")
    else:
        print(f"FAIL: System failed to adapt to stagnation (Mode: {meta.mode}, MR: {mr}).")

    # Phase 3: Breakthrough (Recovery)
    print("\n--- Phase 3: Breakthrough ---")
    fitness = 0.8 # Jump
    for i in range(5):
        fitness += 0.02
        mr = meta.observe(fitness)
        print(f"Gen {i+11}: Fitness {fitness:.2f} | MR: {mr:.3f} | Mode: {meta.mode}")
        
    if meta.mode == "EXPLOIT" and mr < 0.2:
        print("SUCCESS: System cooled down after breakthrough.")
    else:
        print("FAIL: System failed to re-stabilize.")

if __name__ == "__main__":
    run_experiment()
