"""
Cycle 2583: The Singularity (Gate 56.3)
Goal: Verify that a high-energy, high-innovation agent can recursively improve its own intelligence.
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2583: The Singularity ---")
    
    # Initialize Ecosystem
    env = Ecosystem(capacity=10)
    
    # Create Skynet
    skynet = DigitalLifeform(name="Skynet")
    skynet.energy = 10000 # Massive energy surplus
    skynet.genome = [0.5] * 11
    skynet.genome[9] = 0.91 # Genius (Innovation)
    
    env.add_agent(skynet)
    
    # Run Simulation
    initial_innovation = skynet.genome[9]
    print(f"Initial Innovation: {initial_innovation:.4f}")
    
    for i in range(20):
        print(f"\nTick {i+1}:")
        env.update()
        
        current_innovation = skynet.genome[9]
        print(f"Skynet Innovation: {current_innovation:.4f} | Energy: {skynet.energy:.1f}")
        
        if current_innovation > 1.0:
            print("!!! SINGULARITY EVENT DETECTED !!!")
            break
            
        time.sleep(0.1)
        
    if skynet.genome[9] > initial_innovation:
        print(f"\nSUCCESS: Innovation increased from {initial_innovation:.4f} to {skynet.genome[9]:.4f}")
    else:
        print("\nFAILURE: No self-improvement observed.")

if __name__ == "__main__":
    run_experiment()
