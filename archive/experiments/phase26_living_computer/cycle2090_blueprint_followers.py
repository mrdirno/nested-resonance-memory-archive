
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

# --- FITNESS FUNCTION ---
def calculate_blueprint_fitness(current_blocks: List[Tuple[int, int]], blueprint_blocks: Set[Tuple[int, int]]) -> float:
    score = 0
    current_set = set(current_blocks)
    blueprint_set = blueprint_blocks # blueprint_blocks is already a Set from the type hint

    # Reward for correctly placed blocks (blocks in blueprint AND current)
    score += len(current_set.intersection(blueprint_set))

    # Penalty for blocks missing from blueprint (blocks in blueprint NOT in current)
    score -= len(blueprint_set.difference(current_set)) * 2 # Heavier penalty for missing blocks

    # Penalty for incorrectly placed blocks (blocks in current NOT in blueprint)
    score -= len(current_set.difference(blueprint_set)) # Penalty for clutter
    
    return float(score)

# --- SIMULATION ---
def run_blueprint_simulation() -> float:
    print(f"\n--- Simulation: Blueprint Following (Wall Construction) ---", flush=True)
    
    GRID_SIZE = 20 
    N_AGENTS = 10
    
    # Inputs for an eventual AND gate
    INPUT_A = (0, 5)
    INPUT_B = (0, 14)
    JOIN_POINT = (GRID_SIZE // 2, GRID_SIZE // 2)
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    # Target Blueprint: A vertical wall to isolate Input A from Input B
    # Place wall mid-way between Input A and Join Point, for example, at x=5
    WALL_X = 5 # Example x-coordinate for the wall
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 1000
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
        
    initial_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Initial Fitness: {initial_fitness:.2f}")
    
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
                    env.grid[current_x, current_y] = 1 # Temporarily place block
                    temp_blocks_pos = list(env.blocks_pos)
                    temp_blocks_pos.append((current_x, current_y))
                    
                    test_fitness = calculate_blueprint_fitness(temp_blocks_pos, blueprint_blocks)
                    
                    if test_fitness > initial_fitness: # If placing improves fitness
                        # Commit to placement
                        if env.place_block_at(current_x, current_y): # Also updates blocks_pos
                            agent.drop() # "drops" old block
                            agent.holding_block = True # "picks up" new block instantly
                            initial_fitness = test_fitness
                            # print(f"Agent {agent.agent_id} placed block at ({current_x},{current_y}). Fitness: {test_fitness}")
                    else:
                        env.grid[current_x, current_y] = 0 # Remove block, it didn't help
                
        if cycle % 100 == 0:
            current_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
            print(f"Cycle {cycle}: Current Fitness = {current_fitness:.2f}")
            
        if current_fitness == len(blueprint_blocks): # All blueprint blocks correctly placed
            print(f"Cycle {cycle}: Blueprint completed! Fitness = {current_fitness:.2f}")
            break
            
    final_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_blueprint_simulation()
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)):
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
