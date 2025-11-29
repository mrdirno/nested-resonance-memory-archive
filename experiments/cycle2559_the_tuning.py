"""
Cycle 2559: The Tuning (Gate 187)
Goal: Verify Metacognitive Reinforcement.
Mechanism:
- Agent Reflects -> Earns Bonus -> Tunes Weights.
- We check if weights change.
"""

import time
import copy
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
    print("--- Cycle 2559: The Tuning ---")
    
    ecosystem = Ecosystem()
    
    # 1. Philosopher (High Innovation, Low Fertility)
    philosopher = DigitalLifeform(name="Philosopher")
    while len(philosopher.genome) < 11: philosopher.genome.append(0.5)
    philosopher.genome[9] = 0.95 # High Innovation
    philosopher.genome[1] = 0.01 # Low Fertility (Stay focused)
    philosopher.energy = 800
    ecosystem.add_agent(philosopher)
    
    # 2. Worker (Low Innovation)
    worker = DigitalLifeform(name="Worker")
    while len(worker.genome) < 11: worker.genome.append(0.5)
    worker.genome[9] = 0.1
    worker.genome[1] = 0.01
    worker.energy = 800
    ecosystem.add_agent(worker)
    
    print(f"Initialized Agents.")
    
    # Snapshot Initial Weights
    p_w_start = get_weights_checksum(philosopher)
    w_w_start = get_weights_checksum(worker)
    
    print(f"Philosopher Weight Checksum (Start): {p_w_start:.4f}")
    print(f"Worker Weight Checksum (Start): {w_w_start:.4f}")
    
    # Run
    for i in range(20):
        print(f"\n--- Tick {i+1} ---")
        print(f"Status: {philosopher.name} (E={philosopher.energy:.1f}, Intent={philosopher.intent})")
        ecosystem.update()
        
    # Check Delta
    p_w_end = get_weights_checksum(philosopher)
    w_w_end = get_weights_checksum(worker)
    
    print(f"\n--- Results ---")
    print(f"Philosopher Weights: {p_w_start:.4f} -> {p_w_end:.4f} (Delta: {p_w_end - p_w_start:.4f})")
    print(f"Worker Weights: {w_w_start:.4f} -> {w_w_end:.4f} (Delta: {w_w_end - w_w_start:.4f})")
    
    if abs(p_w_end - p_w_start) > 0.0001:
        print("SUCCESS: Philosopher tuned their brain.")
    else:
        print("FAILURE: Philosopher brain static.")
        
    if abs(w_w_end - w_w_start) < 0.0001:
        print("SUCCESS: Worker brain static (as expected).")
    else:
        print("FAILURE: Worker brain mutated unexpectedly.")

if __name__ == "__main__":
    run_experiment()
