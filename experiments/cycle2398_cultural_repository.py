"""
Cycle 2398: Cultural Repository (The Cultural Ratchet)
Role: The Historian
Responsibility: Demonstrate knowledge persistence across generations via a shared repository.
Reference: Tomasello, M. (1999). The Cultural Origins of Human Cognition.
"""

import random
import numpy as np
import matplotlib.pyplot as plt

class Library:
    def __init__(self):
        self.knowledge_base = [] # List of (idea_value, fitness)
        
    def publish(self, idea_value, fitness):
        """Add high-quality ideas to the library."""
        self.knowledge_base.append((idea_value, fitness))
        # Keep only the best ideas (Capacity limit)
        self.knowledge_base.sort(key=lambda x: x[1], reverse=True)
        self.knowledge_base = self.knowledge_base[:10] # Top 10 ideas persist
        
    def read(self):
        """Retrieve the best available knowledge."""
        if not self.knowledge_base:
            return 0.0 # No knowledge yet
        # Return the best idea's value
        return self.knowledge_base[0][0]

class Agent:
    def __init__(self, generation, library):
        self.generation = generation
        self.library = library
        self.age = 0
        self.lifespan = 20
        
        # Cultural Learning: Start from the best known idea, not zero
        self.knowledge = self.library.read()
        
    def live(self):
        self.age += 1
        
        # Innovation: Try to improve current knowledge
        # Small random variation (mutation)
        innovation = random.gauss(0, 1.0)
        
        # If innovation is positive, we improved
        if innovation > 0:
            self.knowledge += innovation
            
    def publish(self):
        # Share knowledge back to library
        self.library.publish(self.knowledge, self.knowledge) # Value and Fitness are same here

def run_simulation(generations=50, agents_per_gen=10):
    print(f"Cycle 2398: Cultural Ratchet (Generations={generations})")
    
    library = Library()
    history_fitness = []
    
    for g in range(generations):
        # Spawn new generation
        agents = [Agent(g, library) for _ in range(agents_per_gen)]
        
        gen_fitness = []
        
        # Life cycle
        for _ in range(20): # Lifespan
            for agent in agents:
                agent.live()
                
        # End of life: Publish and Record
        for agent in agents:
            agent.publish()
            gen_fitness.append(agent.knowledge)
            
        avg_fitness = np.mean(gen_fitness)
        best_fitness = np.max(gen_fitness)
        history_fitness.append(avg_fitness)
        
        print(f"Gen {g}: Avg Fitness = {avg_fitness:.2f}, Best = {best_fitness:.2f}, Library Best = {library.read():.2f}")
        
    # Validation: Did we ratchet up?
    start_fitness = history_fitness[0]
    end_fitness = history_fitness[-1]
    
    print(f"\nEvolution: {start_fitness:.2f} -> {end_fitness:.2f}")
    
    if end_fitness > start_fitness * 5:
        print("SUCCESS: Cultural Ratchet confirmed. Knowledge accumulated.")
        return True
    else:
        print("FAIL: Knowledge stagnation.")
        return False

if __name__ == "__main__":
    run_simulation()
