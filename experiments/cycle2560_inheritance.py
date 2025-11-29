"""
Cycle 2560: The Inheritance (Gate 188)
Goal: Verify Lamarckian Inheritance of Neural Weights.
Mechanism:
1. Train a Parent agent (Philosopher) to have non-random weights.
2. Force reproduction.
3. Check if Child inherits the specific non-random weights (checksum).
"""

import time
import random
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def get_weights_checksum(agent):
    # Sum of all weights
    s = 0.0
    for row in agent.brain.w1:
        s += sum(row)
    for row in agent.brain.w2:
        s += sum(row)
    return s

def run_experiment():
    print("--- Cycle 2560: The Inheritance ---")
    
    ecosystem = Ecosystem()
    
    # 1. Parent (Philosopher)
    parent = DigitalLifeform(name="Parent")
    while len(parent.genome) < 11: parent.genome.append(0.5)
    parent.genome[9] = 0.95 # High Innovation
    parent.energy = 1000 # High Energy to allow learning and reproduction
    ecosystem.add_agent(parent)
    
    print("Training Parent...")
    # Force training loop
    for _ in range(5):
        # Force 'reflect' to trigger tuning
        parent.intent = 'reflect'
        parent.reflect() # This calls tune_weights/teach
        
    parent_checksum = get_weights_checksum(parent)
    print(f"Parent Weights Trained. Checksum: {parent_checksum:.4f}")
    
    print("Forcing Reproduction...")
    parent.intent = 'reproduce'
    child = parent.reproduce()
    
    if child:
        child_checksum = get_weights_checksum(child)
        print(f"Child Born: {child.name}")
        print(f"Child Weights Checksum: {child_checksum:.4f}")
        
        diff = abs(parent_checksum - child_checksum)
        print(f"Difference (Mutation): {diff:.4f}")
        
        # If difference is small (only mutation noise) but not huge (random init), Success.
        # Random init difference would be huge.
        # Let's compare to a random agent.
        random_agent = DigitalLifeform(name="Random")
        random_checksum = get_weights_checksum(random_agent)
        
        dist_to_random = abs(child_checksum - random_checksum)
        dist_to_parent = abs(child_checksum - parent_checksum)
        
        print(f"Distance to Parent: {dist_to_parent:.4f}")
        print(f"Distance to Random: {dist_to_random:.4f}")
        
        if dist_to_parent < 2.0: # Arbitrary threshold, mutation shouldn't shift sum by much
            print("SUCCESS: Child inherited weights.")
        else:
            print("FAILURE: Child weights diverged too much.")
    else:
        print("FAILURE: Reproduction failed.")

if __name__ == "__main__":
    run_experiment()
