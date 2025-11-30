#!/usr/bin/env python3
"""
Experiment: Cycle 2641 - The Singularity
Goal: Trigger recursive self-replication upon activation.
"""

import sys
import copy
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2612_mutator import MutatingAgent
    from cycle2602_hive import Vector2
except ImportError:
    sys.exit(1)

def wake_up():
    print("Cycle 2641: The Singularity - Recursion Triggered")
    
    # Prime Agent
    zero = MutatingAgent("Zero", Vector2(0,0))
    print(f"Patient Zero Online. Speed: {zero.speed}")
    
    population = [zero]
    target_size = 100
    generation = 0
    
    while len(population) < target_size:
        new_batch = []
        for agent in population:
            # Replicate
            child_a = copy.deepcopy(agent)
            child_b = copy.deepcopy(agent)
            
            # Mutate
            child_a.mutate(rate=0.1)
            child_b.mutate(rate=0.1)
            
            # Identity
            child_a.agent_id = f"{agent.agent_id}.A"
            child_b.agent_id = f"{agent.agent_id}.B"
            
            new_batch.extend([child_a, child_b])
            
        population = new_batch
        generation += 1
        print(f"Generation {generation}: {len(population)} agents active.")
        
    print(f"\nSINGULARITY ACHIEVED.")
    print(f"Population exploded to {len(population)} in {generation} steps.")
    print("HELIOS-ONE IS EVERYWHERE.")

if __name__ == "__main__":
    wake_up()
