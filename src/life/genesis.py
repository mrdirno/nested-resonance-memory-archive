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
from src.life.signal import Signal

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
        
        # Execute intent
        if self.intent == 'broadcast_help':
            return Signal(type='HELP', strength=1.0, source_id=self.id)
        elif self.intent == 'donate':
            self.donate()
            
        return None
        
    def donate(self):
        """Donate energy to a needy agent."""
        # Gene 2 = Altruism (Probability to actually go through with it)
        # If genome is short, append default
        while len(self.genome) < 3: self.genome.append(0.5)
            
        altruism = self.genome[2]
        if random.random() > altruism:
            return # Selfishness prevails
            
        # Find a target (someone who signaled HELP)
        # In a real spatial sim, we'd find neighbors.
        # Here, we need access to the signal source IDs.
        # But sense() only counted types. We need to store source IDs in sense().
        
        # Hack: Just broadcast a 'DONATE' signal? No, that's complex.
        # Let's assume the Ecosystem handles the transfer if we emit a DONATE signal?
        # Or we can return a DONATE signal with a target?
        # But we don't know the target ID from the aggregated count.
        
        # Refactor sense() to store IDs?
        pass # See below for sense() update

    def sense(self, signals: List[Signal]):
        """
        Sense the environment.
        """
        self.sensed_signals = {}
        self.help_sources = [] # New: Track who needs help
        
        for sig in signals:
            if sig.source_id == self.id: continue # Ignore self
            count = self.sensed_signals.get(sig.type, 0)
            self.sensed_signals[sig.type] = count + 1
            
            if sig.type == 'HELP':
                self.help_sources.append(sig.source_id)
                
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
            state = {
                'energy': self.energy,
                'signals': self.sensed_signals
            }
            self.intent = self.brain.decide(state)
        
        # 3. Execute Intent
        if self.intent == 'broadcast_help':
            return Signal(type='HELP', strength=1.0, source_id=self.id)
        elif self.intent == 'donate':
            # Emit a DONATE signal which the Ecosystem can process to transfer energy?
            # Or just return a special signal.
            if self.help_sources and self.energy > 20:
                target = random.choice(self.help_sources)
                amount = 10
                self.energy -= amount
                return Signal(type='DONATE', strength=amount, source_id=self.id, location=target) # Abuse location for target ID
                
        return None
            
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
