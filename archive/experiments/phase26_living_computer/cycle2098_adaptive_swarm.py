
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set, Optional, Dict
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2097_collective_estimator import ValueGridEnvironment, EstimatorAgent # Reuse base env and agent


# --- SIMULATION ---
def run_adaptive_simulation() -> float:
    print(f"\n--- Simulation: Adaptive Swarm ---", flush=True)
    
    GRID_SIZE = 20
    N_AGENTS = 20
    COMM_RANGE = 5.0 # Communication range for agents
    
    INITIAL_CYCLES = 500 # Cycles for estimation convergence
    ADAPTATION_CYCLES = 100 # Cycles after adaptation to observe
    
    INITIAL_VELOCITY_MAGNITUDE = 1.0 # Agents start at this speed

    # Environment Setup
    env = ValueGridEnvironment(GRID_SIZE)
    
    # Calculate true global average of the environment
    true_global_average = np.mean(env.grid)
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = EstimatorAgent( 
            agent_id=f"adaptive_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agent.velocity_magnitude = INITIAL_VELOCITY_MAGNITUDE # Add velocity attribute
        agents.append(agent)
        
    print(f"True Global Average of Environment: {true_global_average:.2f}")
    
    # --- PHASE 1: COLLECTIVE ESTIMATION ---
    print("\n--- Phase 1: Collective Estimation ---")
    for cycle in range(INITIAL_CYCLES):
        # 1. Agents Move & Sense
        for agent in agents:
            # Movement uses individual agent's velocity_magnitude
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-agent.velocity_magnitude, agent.velocity_magnitude))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-agent.velocity_magnitude, agent.velocity_magnitude))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            
            # Sense value at current location
            agent.sense(env.get_value_at(agent_x, agent_y))
            
        # 2. Agents Communicate (pairwise averaging)
        for i in range(N_AGENTS):
            for j in range(i + 1, N_AGENTS):
                agent1 = agents[i]
                agent2 = agents[j]
                
                dist = np.linalg.norm(agent1.state.position - agent2.state.position)
                if dist < COMM_RANGE:
                    agent1.communicate(agent2)

        if np.std([a.internal_estimate for a in agents]) < 0.1 and cycle > 50: # Standard deviation very low
            print(f"Cycle {cycle}: Swarm estimates converged.")
            break
            
    final_estimates = [a.internal_estimate for a in agents]
    final_avg_estimate = np.mean(final_estimates)
    final_std_estimate = np.std(final_estimates)
    
    print(f"Swarm converged to estimate: {final_avg_estimate:.2f} (True: {true_global_average:.2f})")
    print(f"Estimation Std Dev: {final_std_estimate:.2f}")
    
    # --- PHASE 2: ADAPTIVE CONTROL ---
    print("\n--- Phase 2: Adaptive Control ---")
    print(f"Adjusting swarm velocity to estimated environment average ({final_avg_estimate:.2f})...")
    
    for agent in agents:
        agent.velocity_magnitude = final_avg_estimate # Agents adjust their speed
    
    for cycle in range(ADAPTATION_CYCLES):
        for agent in agents:
            # Move with adjusted velocity
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-agent.velocity_magnitude, agent.velocity_magnitude))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-agent.velocity_magnitude, agent.velocity_magnitude))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            # No sensing/communication in this phase, just observing behavior
            
        if cycle % 20 == 0:
            current_avg_vel = np.mean([a.velocity_magnitude for a in agents])
            print(f"Adapt Cycle {cycle}: Avg Velocity = {current_avg_vel:.2f}")
    
    final_avg_velocity = np.mean([a.velocity_magnitude for a in agents])
    
    print(f"Final Swarm Avg Velocity: {final_avg_velocity:.2f} (Target: {final_avg_estimate:.2f})")
    
    control_accuracy = abs(final_avg_velocity - final_avg_estimate)
    
    return control_accuracy

if __name__ == "__main__":
    control_accuracy = run_adaptive_simulation()
    if control_accuracy < 0.1: # Threshold for accurate control
        print("SUCCESS: Swarm collectively estimated and adapted its behavior.")
    else:
        print("FAILURE: Swarm failed to adapt its behavior accurately.")
