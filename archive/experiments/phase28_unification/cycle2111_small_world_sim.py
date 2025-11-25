
import sys
import os
import random
import numpy as np
from typing import List

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2110_multi_scale_sim import MultiScaleAgent

def run_small_world_sim() -> bool:
    print(f"\n--- Simulation: Small-World Integration ---", flush=True)
    
    N_AGENTS = 50
    CYCLES = 200
    LONG_RANGE_PROB = 0.05 # 5% chance of interacting with distant agent
    
    agents = []
    for i in range(N_AGENTS):
        strat = "Cooperator" if i < 30 else "Defector"
        estimate = float(i)
        
        agent = MultiScaleAgent(
            agent_id=f"m_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.random.rand(3) * 20.0
        )
        agent.strategy = strat
        agent.estimate = estimate
        
        for j in range(N_AGENTS):
            j_strat = "Cooperator" if j < 30 else "Defector"
            score = 1.0 if j_strat == "Cooperator" else -1.0
            agent.memory[f"m_{j}"] = score * 5.0
            
        agents.append(agent)
        
    for cycle in range(CYCLES):
        # 1. Move (Physics)
        for agent in agents:
            best_neighbor = None
            best_affinity = -999.0
            for other in agents:
                if agent == other: continue
                affinity = agent.calculate_unified_affinity(other, alpha=0.5)
                if affinity > best_affinity:
                    best_affinity = affinity
                    best_neighbor = other
            if best_neighbor and best_affinity > 0:
                direction = best_neighbor.state.position - agent.state.position
                dist = np.linalg.norm(direction)
                if dist > 0.1:
                    agent.move((direction / dist) * 0.5)

        # 2. Interact (With Small-World Links)
        for agent in agents:
            neighbors = []
            for other in agents:
                if agent == other: continue
                dist = np.linalg.norm(agent.state.position - other.state.position)
                
                # Condition A: Local Neighbor
                is_local = dist < 2.0
                
                # Condition B: Long-Range Link (Random chance)
                is_long_range = random.random() < LONG_RANGE_PROB
                
                if is_local or is_long_range:
                    affinity = agent.calculate_unified_affinity(other, alpha=0.5)
                    if affinity > 0.0: # Must still be trusted
                        neighbors.append(other)
            
            agent.compute(neighbors)
            
        # 3. Measure
        coops = [a for a in agents if a.strategy == "Cooperator"]
        estimates = [a.estimate for a in coops]
        std_dev = np.std(estimates)
        
        if cycle % 50 == 0:
            print(f"Cycle {cycle}: Coop StdDev {std_dev:.4f}")
            
    final_std = std_dev
    print(f"Final Coop StdDev: {final_std:.4f}")
    
    if final_std < 0.1:
        print("SUCCESS: Small-World Networks Enabled Global Consensus.")
        return True
    else:
        print("FAILURE: Did not converge.")
        return False

if __name__ == "__main__":
    run_small_world_sim()
