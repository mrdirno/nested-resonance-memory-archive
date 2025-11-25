
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent
from src.experiments.cycle2088_analog_and_gate import AndGateEnvironment # Reuse the env for pathfinding


# --- BLUEPRINT DEFINITION ---
def generate_wall_blueprint(grid_size: int, wall_x: int) -> Set[Tuple[int, int]]:
    blueprint = set()
    for y in range(grid_size):
        blueprint.add((wall_x, y))
    return blueprint

# --- FITNESS FUNCTION (REVISED) ---
def calculate_blueprint_fitness(current_blocks: List[Tuple[int, int]], blueprint_blocks: Set[Tuple[int, int]]) -> float:
    score = 0
    current_set = set(current_blocks)
    
    # Reward for correctly placed blocks
    score += len(current_set.intersection(blueprint_blocks))

    # Penalty for incorrectly placed blocks (clutter) - less harsh
    score -= len(current_set.difference(blueprint_blocks)) * 0.5 
    
    # No penalty for missing blocks from blueprint initially. We want to encourage any correct placement.
    
    return float(score)

# --- SIMULATION ---
def run_tolerant_builder_simulation() -> float:
    print(f"\n--- Simulation: Tolerant Builder (Wall Construction) ---", flush=True)
    
    GRID_SIZE = 20 
    N_AGENTS = 10
    
    INPUT_A = (0, 5)
    INPUT_B = (0, 14)
    JOIN_POINT = (GRID_SIZE // 2, GRID_SIZE // 2)
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    # Target Blueprint: A vertical wall to isolate Input A from Input B
    # Place wall mid-way between Input A and Join Point, for example, at x=5
    WALL_X = 5 # Example x-coordinate for the wall
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 2000 # More cycles for exploration
    VELOCITY_MAGNITUDE = 1.0 
    
    # Environment Setup: Start empty
    env = AndGateEnvironment(GRID_SIZE, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT, num_initial_blocks=0)
    
    # Special points that agents cannot place blocks on
    special_points = {INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT}

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
        
    current_global_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Initial Fitness: {current_global_fitness:.2f}")
    
    for cycle in range(CYCLES):
        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: Try to improve fitness by placing blocks
            if agent.holding_block:
                # If on an empty spot, try to place it
                if env.grid[current_x, current_y] == 0 and \
                   (current_x, current_y) not in special_points:
                    
                    # Calculate fitness if block is placed here
                    # Temporarily add the block to blocks_pos for fitness calculation
                    temp_blocks_pos = list(env.blocks_pos)
                    temp_blocks_pos.append((current_x, current_y))
                    
                    test_fitness = calculate_blueprint_fitness(temp_blocks_pos, blueprint_blocks)
                    
                    if test_fitness > current_global_fitness: # If placing improves fitness
                        # Commit to placement
                        if env.place_block_at(current_x, current_y): # Also updates env.blocks_pos
                            agent.drop() # "drops" old block
                            agent.holding_block = True # "picks up" new block instantly
                            current_global_fitness = test_fitness
                            # print(f"Agent {agent.agent_id} placed block at ({current_x},{current_y}). Fitness: {test_fitness}")
                    # else: env.grid[current_x, current_y] = 0 # No need to revert env.grid; it was never changed if not committed
                
        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Current Fitness = {current_global_fitness:.2f}")
            
        if current_global_fitness >= len(blueprint_blocks): # All blueprint blocks correctly placed and no clutter
            print(f"Cycle {cycle}: Blueprint completed! Fitness = {current_global_fitness:.2f}")
            break
            
    final_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_tolerant_builder_simulation()
    # Correct condition for success, considering negative penalties for clutter
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)) * 0.9: # Allow some minor clutter, or perfect match
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
