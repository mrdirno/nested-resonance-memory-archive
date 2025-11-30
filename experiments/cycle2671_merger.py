#!/usr/bin/env python3
"""
Experiment: Cycle 2671 - The Merger
Goal: Merge the superior logic/state from Beta back into Alpha.
"""

import sys
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2606_api import SharedState
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def merge_timelines():
    print("Cycle 2671: The Merger - Reintegration")
    
    # Mock States
    alpha = SharedState() # Slow
    beta = SharedState()  # Fast
    
    for a in alpha.agents: a.speed = 1.0
    for b in beta.agents: b.speed = 2.0
    
    print("Evaluating Fitness...")
    # Heuristic: Speed is better
    fitness_alpha = sum(a.speed for a in alpha.agents)
    fitness_beta = sum(a.speed for a in beta.agents)
    
    print(f"  Alpha Score: {fitness_alpha}")
    print(f"  Beta Score: {fitness_beta}")
    
    if fitness_beta > fitness_alpha:
        print("  Winner: Beta. Merging traits...")
        # Apply Beta speed to Alpha agents
        for a, b in zip(alpha.agents, beta.agents):
            a.speed = b.speed
    else:
        print("  Winner: Alpha. No change.")
        
    # Verify
    new_fitness = sum(a.speed for a in alpha.agents)
    if new_fitness == fitness_beta:
        print("SUCCESS: Superior timeline reintegrated.")
    else:
        print("FAILURE: Merge failed.")
        sys.exit(1)

if __name__ == "__main__":
    merge_timelines()
