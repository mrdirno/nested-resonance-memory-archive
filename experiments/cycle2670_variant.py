#!/usr/bin/env python3
"""
Experiment: Cycle 2670 - The Variant
Goal: Apply mutation to the Beta timeline.
"""

import sys
import copy
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2606_api import SharedState
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def mutate_timeline():
    print("Cycle 2670: The Variant - Timeline Divergence")
    
    # Setup Baseline
    alpha = SharedState()
    beta = SharedState()
    
    # Manual Deep Copy of Agents
    alpha.agents = [HiveAgent(f"A_{i}", Vector2(0,0)) for i in range(5)]
    beta.agents = [HiveAgent(f"B_{i}", Vector2(0,0)) for i in range(5)]
    
    # Mutate Beta
    print("Applying Speed Mutation to Beta (Factor 2.0)...")
    for agent in beta.agents:
        agent.speed *= 2.0
        
    # Run Simulation
    target = Vector2(100, 0)
    steps = 10
    
    print("Simulating 10 steps...")
    for _ in range(steps):
        for a in alpha.agents: a.update(target)
        for b in beta.agents: b.update(target)
        
    # Compare Distance
    dist_alpha = alpha.agents[0].position.x
    dist_beta = beta.agents[0].position.x
    
    print(f"Alpha Progress: {dist_alpha:.2f}")
    print(f"Beta Progress: {dist_beta:.2f}")
    
    if dist_beta > dist_alpha * 1.5:
        print("SUCCESS: Beta variant significantly outperformed Alpha.")
    else:
        print("FAILURE: Mutation ineffective.")
        sys.exit(1)

if __name__ == "__main__":
    mutate_timeline()
