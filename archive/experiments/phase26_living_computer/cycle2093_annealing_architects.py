
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
def run_annealing_simulation() -> float:
    print(f"\n--- Simulation: Annealing Architects ---", flush=True)
    
    N_AGENTS = 10
    N_INITIAL_LOOSE_BLOCKS = 30 # Number of blocks to start with, agents will move them
    
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 2000 
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
        agent = RelocatorAgent( # Use RelocatorAgent
            agent_id=f"relocator_{i}",
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
                # Try to pick up a block from the grid at current position
                block_to_pickup_coords = env.get_block_at(current_x, current_y) # This returns tuple if block exists
                
                if block_to_pickup_coords: # This is the block at agent's position
                    # Temporarily remove block_to_pickup_coords from blocks_pos for fitness calculation
                    # and from env.grid
                    env.grid[current_x, current_y] = 0 # Temporarily remove from grid
                    
                    # Ensure block_to_pickup_coords is actually in env.blocks_pos before trying to remove
                    # This check is for robustness, as it should be there if env.grid[current_x, current_y] was 1
                    if block_to_pickup_coords in env.blocks_pos:
                        env.blocks_pos.remove(block_to_pickup_coords) # Simulate removal from blocks_pos list
                    else: # This indicates an inconsistency
                        print(f"Warning: Block at {block_to_pickup_coords} in grid but not in blocks_pos. Cycle {cycle}")
                        env.grid[current_x, current_y] = 1 # Restore grid state
                        continue # Skip this agent's turn if inconsistent

                    test_fitness_after_removal = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
                    
                    commit_pickup = False
                    if test_fitness_after_removal > current_global_fitness:
                        commit_pickup = True
                    elif temperature > 0:
                        acceptance_probability = np.exp((test_fitness_after_removal - current_global_fitness) / temperature)
                        if random.random() < acceptance_probability:
                            commit_pickup = True
                    
                    if commit_pickup:
                        # block is already removed from blocks_pos and grid
                        agent.pick_up_from_grid(block_to_pickup_coords) # Agent now holding it
                        current_global_fitness = test_fitness_after_removal
                    else: # Revert temporary removal (put block back)
                        env.blocks_pos.append(block_to_pickup_coords) # Put back in blocks_pos
                        env.grid[current_x, current_y] = 1 # Put block back in grid
            
            # --- If holding a block ---
            else: 
                # Try to drop it at current_x, current_y
                if env.grid[current_x, current_y] == 0 and (current_x, current_y) not in special_points:
                    
                    # Temporarily add the block to blocks_pos list and env.grid for fitness calc
                    env.grid[current_x, current_y] = 1 
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
                        if env.place_block_at(current_x, current_y): # This adds to blocks_pos and updates grid
                            agent.drop_on_grid() # Agent is now empty-handed
                            current_global_fitness = test_fitness_after_placement
                    else: # Don't commit, revert temporary placement. Agent still holding block.
                        env.grid[current_x, current_y] = 0 
                
        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Current Fitness = {current_global_fitness:.2f}, Temp = {temperature:.2f}")
            
        if current_global_fitness >= len(blueprint_blocks): # All blueprint blocks correctly placed and no clutter
            print(f"Cycle {cycle}: Blueprint completed! Fitness = {current_global_fitness:.2f}")
            break
            
    final_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_annealing_simulation()
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)) * 0.95: # Allow very minor clutter
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
