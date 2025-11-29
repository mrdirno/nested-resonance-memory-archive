"""
Cycle 2558: The Mirror (Gate 186)
Goal: Allow agents to inspect their own internal state via a "Mirror".
Mechanism:
- Agent chooses 'reflect' action (based on Innovation).
- `reflect()` method prints stats and awards energy bonus.
"""

import time
import random
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2558: The Mirror ---")
    
    # Initialize Ecosystem
    ecosystem = Ecosystem()
    
    # 1. Create a Philosopher (High Innovation)
    philosopher = DigitalLifeform(name="Philosopher")
    # Manually set Innovation (Gene 9) to 0.95
    while len(philosopher.genome) < 10: philosopher.genome.append(0.5)
    philosopher.genome[9] = 0.95 
    philosopher.energy = 400 # Sufficient energy
    ecosystem.add_agent(philosopher)
    
    # 2. Create a Worker (Low Innovation)
    worker = DigitalLifeform(name="Worker")
    while len(worker.genome) < 10: worker.genome.append(0.5)
    worker.genome[9] = 0.1
    worker.energy = 400
    ecosystem.add_agent(worker)
    
    print(f"Initialized Agents:")
    print(f"- {philosopher.name}: Innovation={philosopher.genome[9]}")
    print(f"- {worker.name}: Innovation={worker.genome[9]}")
    
    # Run Simulation
    ticks = 50
    reflection_count = 0
    
    for i in range(ticks):
        print(f"\n--- Tick {i+1} ---")
        
        # Manually override intent for testing if it doesn't trigger naturally
        # But let's see if the utility logic works first.
        # Utility logic: options['reflect'] = 50 * innovation (if > 0.8 and energy > 300)
        # Philosopher: 50 * 0.95 = 47.5.
        # Move score: ~60. Forage score: ~60.
        # It might not win against Forage/Move if energy is lowish.
        # Let's boost Philosopher energy to make survival score low.
        if philosopher.energy < 800: philosopher.energy = 900 
        
        ecosystem.update()
        
        # Check log output (visual) or check energy changes
        # We can't easily check stdout here programmatically without redirecting, 
        # so we'll infer success if the Philosopher gains the specific bonus.
        # Bonus is +5.
        
    print("\n--- Experiment Complete ---")

if __name__ == "__main__":
    run_experiment()
