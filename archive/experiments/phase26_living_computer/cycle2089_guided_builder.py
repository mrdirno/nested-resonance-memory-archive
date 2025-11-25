
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Optional
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent
from src.experiments.cycle2088_analog_and_gate import AndGateEnvironment # Reuse the env for pathfinding


# --- SIMULATION ---
def run_guided_builder_simulation() -> float:
    print(f"\n--- Simulation: Guided Builder (Input Isolation) ---", flush=True)
    
    GRID_SIZE = 20 
    N_AGENTS = 10
    
    INPUT_A = (0, 5)
    INPUT_B = (0, 14)
    JOIN_POINT = (GRID_SIZE // 2, GRID_SIZE // 2)
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    CYCLES = 1000
    VELOCITY_MAGNITUDE = 1.0 
    
    # Environment Setup: Start empty
    env = AndGateEnvironment(GRID_SIZE, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT, num_initial_blocks=0)
    
    # Calculate midpoint between A and B
    midpoint_ab = np.array([
        (INPUT_A[0] + INPUT_B[0]) / 2,
        (INPUT_A[1] + INPUT_B[1]) / 2,
        0.0
    ])
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = OptimizerAgent( # OptimizerAgent has .holding_block
            agent_id=f"builder_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agent.holding_block = True # Agents start with a block
        agents.append(agent)
        
    current_ab_isolated = not env._has_path_internal(env.input_A, env.input_B)
    print(f"Initial A-B isolated: {current_ab_isolated}")
    
    for cycle in range(CYCLES):
        if not env._has_path_internal(env.input_A, env.input_B):
            print(f"Cycle {cycle}: Input A isolated from B!")
            return 1.0 # Success
            
        for agent in agents:
            # Agent's current grid position
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Try to place a block (always holding one)
            if env.grid[current_x, current_y] == 0 and \
               (current_x, current_y) != env.input_A and (current_x, current_y) != env.input_B and \
               (current_x, current_y) != env.join_point and (current_x, current_y) != env.output_point:
                
                env.grid[current_x, current_y] = 1 # Temporarily place block
                
                if not env._has_path_internal(env.input_A, env.input_B): # If placing block isolates A from B
                    # Commit to placement
                    if env.place_block_at(current_x, current_y): # Also updates blocks_pos
                        agent.drop() # "drops" old block
                        agent.holding_block = True # "picks up" new block instantly
                        # print(f"Agent {agent.agent_id} placed block at ({current_x},{current_y}). A-B isolated.")
                        return 1.0 # Success!
                else:
                    env.grid[current_x, current_y] = 0 # Remove block, it didn't help isolate A-B
            
            # Move randomly for exploration if no good placement or not on valid spot
            # Or move towards midpoint to build a wall between A and B
            direction = midpoint_ab - agent.state.position
            norm = np.linalg.norm(direction)
            if norm > 0:
                move_vec = (direction / norm) * VELOCITY_MAGNITUDE
                agent.move(move_vec)
            else:
                # Random walk if already at midpoint
                theta = random.uniform(0, 2*np.pi)
                dx = VELOCITY_MAGNITUDE * np.cos(theta)
                dy = VELOCITY_MAGNITUDE * np.sin(theta)
                agent.move(np.array([dx, dy, 0.0]))
            
            # Ensure agent stays within grid boundaries
            agent.state.position[0] = max(0, min(GRID_SIZE-1, agent.state.position[0]))
            agent.state.position[1] = max(0, min(GRID_SIZE-1, agent.state.position[1]))

        if cycle % 100 == 0:
            print(f"Cycle {cycle}: A-B isolated: {not env._has_path_internal(env.input_A, env.input_B)}")
            
    final_isolation = not env._has_path_internal(env.input_A, env.input_B)
    print(f"Final A-B isolated: {final_isolation}")
    
    return float(final_isolation)

if __name__ == "__main__":
    final_score = run_guided_builder_simulation()
    if final_score >= 1.0:
        print("SUCCESS: Swarm constructed an isolation wall.")
    else:
        print("FAILURE: Swarm failed to construct an isolation wall.")
