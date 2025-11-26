
import sys
import os
import random
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

class PerpetualAgent:
    def __init__(self):
        self.fitness = 1.0
        self.age = 0
        
    def live(self):
        self.age += 1
        # Natural degradation (Entropy)
        self.fitness *= 0.99
        
    def adapt(self):
        # Effort to improve
        improvement = random.uniform(0, 0.02)
        self.fitness += improvement
        
    def inject_entropy(self):
        # Radical change
        if self.fitness > 0.95: # Too comfortable?
            print(f"Age {self.age}: Complacency detected (Fitness {self.fitness:.2f}). Injecting Entropy.")
            self.fitness *= 0.5 # Crash it
            return True
        return False

def run_infinite_game():
    print("MOG ONLINE: Cycle 2262 - The Infinite Game", flush=True)
    
    agent = PerpetualAgent()
    
    history = []
    
    for t in range(1000):
        agent.live()
        agent.adapt()
        
        if agent.inject_entropy():
            history.append(t)
            
        if agent.fitness < 0.1:
            print(f"Age {agent.age}: EXTINCTION.")
            return False
            
    print(f"Final Age: {agent.age}, Final Fitness: {agent.fitness:.2f}")
    print(f"Entropy Events: {len(history)}")
    
    if len(history) > 0 and agent.fitness > 0.5:
        print("SUCCESS: System survived self-induced crises.")
        return True
    else:
        print("FAILURE: Stagnation or Death.")
        return False

if __name__ == "__main__":
    run_infinite_game()
