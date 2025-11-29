"""
Cycle 2581: The Optimizer (Gate 56.1)
Goal: Verify that the modular kernel architecture functions correctly and allows for introspection.
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

class OptimizerAgent(DigitalLifeform):
    def inspect_kernel(self, ecosystem):
        print(f"🔍 {self.name} INSPECTING KERNEL...")
        phases = ecosystem.kernel_phases
        for i, phase in enumerate(phases):
            print(f"   Phase {i}: {phase.__name__}")
        return len(phases)

def run_experiment():
    print("--- Cycle 2581: The Optimizer (Kernel Validation) ---")
    
    # Initialize Ecosystem
    env = Ecosystem(capacity=20)
    
    # Create Agent
    neo = OptimizerAgent(name="TheOptimizer")
    neo.energy = 400
    env.add_agent(neo)
    
    # Add a mate
    eve = DigitalLifeform(name="Eve")
    eve.energy = 400
    env.add_agent(eve)
    
    # Run Simulation
    print("\n[Running Simulation]")
    for i in range(5):
        print(f"Tick {i+1}:")
        env.update()
        print(f"Population: {len(env.agents)}")
        
    # Test Introspection
    print("\n[Testing Introspection]")
    phase_count = neo.inspect_kernel(env)
    
    if phase_count > 0:
        print(f"\nSUCCESS: Kernel has {phase_count} phases and is accessible.")
    else:
        print("\nFAILURE: Kernel phases not found.")

    if len(env.agents) >= 2:
         print("SUCCESS: Population stability verified.")
    else:
         print("WARNING: Population instability.")

if __name__ == "__main__":
    run_experiment()
