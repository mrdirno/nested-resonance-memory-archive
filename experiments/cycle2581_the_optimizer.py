"
Cycle 2581: The Optimizer (Gate 56.1)
Goal: Verify that the modular kernel architecture functions correctly (Regression Test).
"

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2581: The Optimizer (Kernel Validation) ---")
    
    # Initialize Ecosystem
    env = Ecosystem(capacity=20)
    
    # Create Adam and Eve
    adam = DigitalLifeform(name="Adam")
    adam.energy = 400
    eve = DigitalLifeform(name="Eve")
    eve.energy = 400
    
    env.add_agent(adam)
    env.add_agent(eve)
    
    # Run Simulation
    for i in range(10):
        print(f"\nTick {i+1}:")
        env.update()
        print(f"Population: {len(env.agents)}")
        
    if len(env.agents) > 2:
        print("\nSUCCESS: Population grew using the modular kernel.")
    else:
        print("\nWARNING: Population did not grow. Check reproduction logic.")

if __name__ == "__main__":
    run_experiment()