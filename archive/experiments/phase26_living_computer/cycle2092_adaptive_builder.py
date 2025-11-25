
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set, Optional
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent
from src.experiments.cycle2088_analog_and_gate import AndGateEnvironment # Reuse the env for pathfinding

# --- Constants for the simulation ---
GRID_SIZE = 20 
WALL_X = 5
INPUT_A = (0, 5)
INPUT_B = (0, 14)
JOIN_POINT = (GRID_SIZE // 2, GRID_SIZE // 2)
OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)

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
    
    # Reward for correctly placed blocks
    score += len(current_set.intersection(blueprint_blocks))

    # Penalty for incorrectly placed blocks (clutter) - less harsh
    score -= len(current_set.difference(blueprint_blocks)) * 0.5 
    
    return float(score)

# --- RELOCATOR AGENT ---
class RelocatorAgent(OptimizerAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.holding_block_coords: Optional[Tuple[int, int]] = None # Store coords of block being held

    def pick_up_from_grid(self, block_coords: Tuple[int, int]):
        self.holding_block_coords = block_coords
        self.holding_block = True # From OptimizerAgent (inherited from BuilderAgent)
        
    def drop_on_grid(self) -> Optional[Tuple[int, int]]:
        coords = self.holding_block_coords
        self.holding_block_coords = None
        self.holding_block = False
        return coords # Return coords of dropped block


# --- SIMULATION ---
def run_adaptive_simulation() -> float:
    print(f"\n--- Simulation: Adaptive Builder (Relocation) ---", flush=True)
    
    N_AGENTS = 10
    N_INITIAL_LOOSE_BLOCKS = 30 # Number of blocks to start with, agents will move them
    
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 2000 # More cycles for exploration
    VELOCITY_MAGNITUDE = 1.0 
    
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
        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: pick up / drop / relocate
            
            # --- If not holding a block ---
            if not agent.holding_block_coords: # Use holding_block_coords for clarity
                # Try to pick up a block from the grid at current position
                block_to_pickup_coords = env.get_block_at(current_x, current_y) # This returns tuple if block exists
                
                if block_to_pickup_coords: # If there's a block here
                    # Temporarily remove and calculate fitness. Agent will always attempt to pick up.
                    if env.remove_block_at(current_x, current_y): # Remove from grid
                        agent.pick_up_from_grid(block_to_pickup_coords) # Agent now holding it
            
            # --- If holding a block ---
            else: 
                # Try to drop it at current_x, current_y
                if env.grid[current_x, current_y] == 0 and (current_x, current_y) not in special_points:
                    
                    # Temporarily add the block to blocks_pos list and env.grid for fitness calc
                    env.grid[current_x, current_y] = 1 
                    temp_blocks_pos = list(env.blocks_pos)
                    temp_blocks_pos.append((current_x, current_y))
                    
                    test_fitness = calculate_blueprint_fitness(temp_blocks_pos, blueprint_blocks)
                    
                    if test_fitness > current_global_fitness: # Commit to placement
                        if env.place_block_at(current_x, current_y): # This adds to blocks_pos and updates grid
                            agent.drop_on_grid() # Agent is now empty-handed
                            current_global_fitness = test_fitness
                            # print(f"Agent {agent.agent_id} placed block at ({current_x},{current_y}). Fitness: {test_fitness}")
                    else: # Don't commit, revert temporary placement. Agent still holding block.
                        env.grid[current_x, current_y] = 0 
                
        if cycle % 100 == 0:
            current_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
            print(f"Cycle {cycle}: Current Fitness = {current_fitness:.2f}")
            
        if current_global_fitness >= len(blueprint_blocks): # All blueprint blocks correctly placed and no clutter
            print(f"Cycle {cycle}: Blueprint completed! Fitness = {current_global_fitness:.2f}")
            break
            
    final_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_adaptive_simulation()
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)) * 0.9: # Allow some minor clutter, or perfect match
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
