
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set, Optional, Dict
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent

# --- ENVIRONMENT ---
class ValueGridEnvironment:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.grid = np.random.rand(grid_size, grid_size) * 100.0 # Random values 0-100
        
    def get_value_at(self, x: int, y: int) -> float:
        return self.grid[x, y]

# --- ESTIMATOR AGENT ---
class EstimatorAgent(OptimizerAgent): # Inherits basic movement from OptimizerAgent
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.internal_estimate: float = 0.0

    def sense(self, env_value: float):
        # When sensing, average with current estimate (more robust against noise/sudden changes)
        # For simple averaging, initialize with sensed value, then just communicate
        # Let's initialize with sensed, then communication takes over
        if self.internal_estimate == 0.0: # Only on first sense, or if reset
            self.internal_estimate = env_value 
        else:
            # Maybe a weighted average to reflect new info vs old
            pass # Keep it simple for now, communication will average

    def communicate(self, other: 'EstimatorAgent'):
        # Simple averaging consensus protocol
        avg = (self.internal_estimate + other.internal_estimate) / 2.0
        self.internal_estimate = avg
        other.internal_estimate = avg

# --- SIMULATION ---
def run_estimator_simulation() -> float:
    print(f"\n--- Simulation: Collective Estimator ---", flush=True)
    
    GRID_SIZE = 20
    N_AGENTS = 20
    COMM_RANGE = 5.0 # Communication range for agents
    
    CYCLES = 500
    VELOCITY_MAGNITUDE = 1.0 

    # Environment Setup
    env = ValueGridEnvironment(GRID_SIZE)
    
    # Calculate true global average of the environment
    true_global_average = np.mean(env.grid)
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = EstimatorAgent( 
            agent_id=f"estimator_{i}",
            energy=10.0, # Not relevant for this sim, just a placeholder
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    print(f"True Global Average: {true_global_average:.2f}")
    
    for cycle in range(CYCLES):
        # 1. Agents Move & Sense
        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
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

        if cycle % 50 == 0:
            current_estimates = [a.internal_estimate for a in agents]
            avg_estimate = np.mean(current_estimates)
            std_estimate = np.std(current_estimates)
            
            print(f"Cycle {cycle}: Avg Est = {avg_estimate:.2f}, Std Dev = {std_estimate:.2f}")
            
        # Check for convergence
        if np.std([a.internal_estimate for a in agents]) < 0.1 and cycle > 50: # Standard deviation very low
            print(f"Cycle {cycle}: Swarm estimates converged.")
            break
            
    final_estimates = [a.internal_estimate for a in agents]
    final_avg_estimate = np.mean(final_estimates)
    final_std_estimate = np.std(final_estimates)
    
    print(f"Final Avg Estimate: {final_avg_estimate:.2f} (True: {true_global_average:.2f})")
    print(f"Final Std Dev: {final_std_estimate:.2f}")
    
    # Measure accuracy: absolute difference from true global average
    accuracy = abs(final_avg_estimate - true_global_average)
    
    return accuracy

if __name__ == "__main__":
    accuracy = run_estimator_simulation()
    if accuracy < 1.0: # Arbitrary threshold for "accurate" 
        print("SUCCESS: Swarm collectively estimated the global average.")
    else:
        print("FAILURE: Swarm failed to estimate the global average accurately.")
