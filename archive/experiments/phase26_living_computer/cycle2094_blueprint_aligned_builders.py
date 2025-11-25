
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set, Optional
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2092_adaptive_builder import RelocatorAgent, calculate_blueprint_fitness, generate_wall_blueprint, AndGateEnvironment, GRID_SIZE, WALL_X, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT

# --- SIMULATION ---
def run_aligned_simulation() -> float:
    print(f"\n--- Simulation: Blueprint Aligned Builders ---", flush=True)
    
    N_AGENTS = 10
    N_INITIAL_LOOSE_BLOCKS = 30 # Number of blocks to start with, agents will move them
    
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 3000 # More cycles for exploration
    VELOCITY_MAGNITUDE = 1.0 
    
    MAX_TEMPERATURE = 10.0 # Initial temperature for annealing

    # Environment Setup: Start empty
    env = AndGateEnvironment(GRID_SIZE, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT, num_initial_blocks=0)
    
    # Populate with initial loose blocks (not part of blueprint, just random clutter)
    for _ in range(N_INITIAL_LOOSE_BLOCKS):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if env.place_block_at(x,y): # Try to place block
                break
    
    # Special points that agents cannot place blocks on
    special_points = {INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT}

    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = RelocatorAgent( 
            agent_id=f"aligned_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    current_global_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Initial Fitness: {current_global_fitness:.2f}")
    
    for cycle in range(CYCLES):
        temperature = MAX_TEMPERATURE * (1 - cycle / CYCLES)
        
        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: pick up / drop / relocate
            
            # --- If not holding a block ---
            if not agent.holding_block_coords: 
                # Prioritize picking up a block that is NOT on the blueprint (clutter)
                block_to_pickup_coords = None
                
                # Check current position first for clutter
                if env.grid[current_x, current_y] == 1 and (current_x, current_y) not in blueprint_blocks:
                    block_to_pickup_coords = (current_x, current_y)
                
                # If not at current pos, scan neighbors for clutter
                if not block_to_pickup_coords:
                    clutter_neighbors = []
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                        nx, ny = current_x + dx, current_y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and env.grid[nx,ny] == 1 and (nx,ny) not in blueprint_blocks:
                            clutter_neighbors.append((nx,ny))
                    if clutter_neighbors:
                        block_to_pickup_coords = random.choice(clutter_neighbors)

                # If no clutter nearby, pick up any block to allow rearrangement (using annealing criteria)
                if not block_to_pickup_coords and env.blocks_pos:
                    block_to_pickup_coords = random.choice(env.blocks_pos) # Random block for potential rearrangement
                
                if block_to_pickup_coords:
                    # Temporarily remove and calculate fitness.
                    temp_blocks_pos_before_pickup = list(env.blocks_pos)
                    if block_to_pickup_coords in temp_blocks_pos_before_pickup:
                        temp_blocks_pos_before_pickup.remove(block_to_pickup_coords)
                    
                    test_fitness_after_pickup = calculate_blueprint_fitness(temp_blocks_pos_before_pickup, blueprint_blocks)
                    
                    # Decide whether to pick up based on annealing
                    commit_pickup = False
                    if test_fitness_after_pickup > current_global_fitness:
                        commit_pickup = True
                    elif temperature > 0:
                        acceptance_probability = np.exp((test_fitness_after_pickup - current_global_fitness) / temperature)
                        if random.random() < acceptance_probability:
                            commit_pickup = True

                    if commit_pickup:
                        if env.remove_block_at(block_to_pickup_coords[0], block_to_pickup_coords[1]): # Actual removal
                            agent.pick_up_from_grid(block_to_pickup_coords)
                            current_global_fitness = test_fitness_after_pickup
                            # print(f"Agent {agent.agent_id} picked up {block_to_pickup_coords}. Fitness {current_global_fitness:.2f}")

            # --- If holding a block ---
            else: 
                # PRIORITIZE BLUEPRINT PLACEMENT
                target_drop_spot = None
                
                # Check current position first for blueprint spot
                if (current_x, current_y) in blueprint_blocks and env.grid[current_x, current_y] == 0 and (current_x, current_y) not in special_points:
                    target_drop_spot = (current_x, current_y)
                
                # If not at current pos, scan neighbors for blueprint spots
                if not target_drop_spot:
                    blueprint_neighbors = []
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                        nx, ny = current_x + dx, current_y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx,ny) in blueprint_blocks and env.grid[nx,ny] == 0 and (nx,ny) not in special_points:
                            blueprint_neighbors.append((nx,ny))
                    if blueprint_neighbors:
                        target_drop_spot = random.choice(blueprint_neighbors)
                
                if target_drop_spot: # Found a blueprint spot! This is high priority
                    # Temporarily place block and calculate fitness. This move should almost always improve.
                    temp_blocks_pos_after_placement = list(env.blocks_pos)
                    temp_blocks_pos_after_placement.append(target_drop_spot)
                    
                    test_fitness_after_placement = calculate_blueprint_fitness(temp_blocks_pos_after_placement, blueprint_blocks)
                    
                    # Commit if it's an improvement or at least not too bad
                    if test_fitness_after_placement >= current_global_fitness: # Always accept blueprint spot if not worse
                        if env.place_block_at(target_drop_spot[0], target_drop_spot[1]):
                            agent.drop_on_grid()
                            current_global_fitness = test_fitness_after_placement
                            # print(f"Agent {agent.agent_id} placed block on blueprint at {target_drop_spot}. Fitness: {current_global_fitness:.2f}")
                    else: # If placing on blueprint somehow makes it worse, revert (shouldn't happen with our fitness)
                        pass # Block still held by agent, will try again
                else:
                    # Fall back to simulated annealing for other empty spots
                    if env.grid[current_x, current_y] == 0 and (current_x, current_y) not in special_points:
                        
                        temp_blocks_pos_after_placement = list(env.blocks_pos)
                        temp_blocks_pos_after_placement.append((current_x, current_y))
                        
                        test_fitness_after_placement = calculate_blueprint_fitness(temp_blocks_pos_after_placement, blueprint_blocks)
                        
                        commit_placement = False
                        if test_fitness_after_placement > current_global_fitness:
                            commit_placement = True
                        elif temperature > 0:
                            acceptance_probability = np.exp((test_fitness_after_placement - current_global_fitness) / temperature)
                            if random.random() < acceptance_probability:
                                commit_placement = True
                                
                        if commit_placement:
                            if env.place_block_at(current_x, current_y):
                                agent.drop_on_grid()
                                current_global_fitness = test_fitness_after_placement
                        # else: # Block still held by agent, try again next cycle
                        #    env.grid[current_x, current_y] = 0 # No need, never temporarily placed in env.grid
                
        if cycle % 100 == 0:
            current_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
            print(f"Cycle {cycle}: Current Fitness = {current_fitness:.2f}, Temp = {temperature:.2f}")
            
        if current_global_fitness >= len(blueprint_blocks): # All blueprint blocks correctly placed and no clutter
            print(f"Cycle {cycle}: Blueprint completed! Fitness = {current_global_fitness:.2f}")
            break
            
    final_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_aligned_simulation()
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)) * 0.95: # Allow very minor clutter
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
