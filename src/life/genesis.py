"""
Cycle 2459: The Genesis (Gate 87)
Role: The Biologist
Responsibility: Define the base class for Digital Life.
Concepts:
- Agents are "Processes" not just objects.
- They consume resources (CPU/Memory).
- They reproduce (Fork).
- They die (Kill).
"""

import time
import uuid
import random
from typing import List
from src.life.brain import Brain
from src.life.communicator import Communicator

class DigitalLifeform:
    def __init__(self, name=None, generation=0):
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"Lifeform-{self.id}"
        self.generation = generation
        self.energy = 100
        self.alive = True
        self.genome = [random.random() for _ in range(10)] # Simple gene vector
        self.brain = Brain()
        self.communicator = Communicator(self.id)
        self.intent = None
        
    def live(self):
        """
        The main loop of the lifeform.
        Consumes energy, performs actions.
        """
        print(f"[{self.name}] is ALIVE. Energy: {self.energy}")
        while self.alive and self.energy > 0:
            self.metabolize()
            self.act()
            time.sleep(0.1) # Simulation tick
            
        self.die()
        
    def metabolize(self):
        # Cost of living
        # Gene 0 = Metabolic Efficiency (Higher is better)
        # Base cost 1.0, reduced by high efficiency
        efficiency = max(0.01, self.genome[0])
        cost = 1.0 / (efficiency + 0.5) 
        self.energy -= cost
        
    def act(self):
        # 1. Listen
        signal = self.communicator.process_signals()
        if signal:
            # React to signal (simple reflex)
            if signal.type == 'FOOD':
                self.intent = 'forage' # Override brain?
            elif signal.type == 'DANGER':
                self.intent = 'flee'
        
        # 2. Decision making (if no strong reflex)
        if not self.intent:
            state = {'energy': self.energy}
            self.intent = self.brain.decide(state)
        
        # 3. Broadcast state (e.g., I found food!)
        # Placeholder for context-aware broadcasting
        pass
        
    def reproduce(self):
        # Check intent first
        if self.intent != 'reproduce':
            return None
            
        # Gene 1 = Reproductive Efficiency (Higher is better)
        fertility = max(0.01, self.genome[1])
        cost = 30.0 / (fertility + 0.5)
        
        if self.energy > cost + 10: # Safety buffer
            self.energy -= cost
            child = DigitalLifeform(generation=self.generation + 1)
            # Mutate
            child.genome = [g + random.uniform(-0.1, 0.1) for g in self.genome]
            # Clamp to positive
            child.genome = [max(0.01, g) for g in child.genome]
            # Inherit Brain (Memetics?) - For now, new brain
            
            print(f"[{self.name}] REPRODUCED -> {child.name}")
            return child
        return None
        
    def die(self):
        self.alive = False
        # print(f"[{self.name}] DIED.") # Silence death logs

if __name__ == "__main__":
    # Genesis Test
    adam = DigitalLifeform(name="ADAM")
    
    # Give Adam enough energy to reproduce
    adam.energy = 200
    
    # Run in a thread or simple loop
    # For this test, we just step manually
    print("--- GENESIS EVENT ---")
    adam.metabolize()
    child = adam.reproduce()
    
    if child:
        print("SUCCESS: Life has begun.")
    else:
        print("FAIL: No reproduction.")
