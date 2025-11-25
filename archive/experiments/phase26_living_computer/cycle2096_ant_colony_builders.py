
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Set, Optional, Dict
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2094_blueprint_aligned_builders import RelocatorAgent, calculate_blueprint_fitness, generate_wall_blueprint, AndGateEnvironment, GRID_SIZE, WALL_X, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT

# --- Constants for the simulation ---
# GRID_SIZE, WALL_X, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT are already imported
LOCK_DURATION = 5 # cycles a block remains locked after a successful move
PHEROMONE_DECAY = 0.01
PHEROMONE_DEPOSIT = 1.0


# --- ENVIRONMENT & CONNECTIVITY (MODIFIED FOR LOCKING & PHEROMONES) ---
class PheromoneEnvironment(AndGateEnvironment): # Inherit from AndGateEnvironment
    def __init__(self, grid_size: int, input_A: Tuple[int, int], input_B: Tuple[int, int], join_point: Tuple[int, int], output_point: Tuple[int, int], num_initial_blocks: int = 0):
        super().__init__(grid_size, input_A, input_B, join_point, output_point, num_initial_blocks)
        self.locked_blocks: Dict[Tuple[int,int], int] = {} # {coords: unlock_cycle}
        self.pheromone_grid = np.zeros((self.grid_size, self.grid_size), dtype=float)

    def unlock_blocks(self, current_cycle: int):
        to_unlock = [coords for coords, unlock_cycle in self.locked_blocks.items() if unlock_cycle <= current_cycle]
        for coords in to_unlock:
            del self.locked_blocks[coords]

    def evaporate_pheromones(self, decay_rate: float):
        self.pheromone_grid *= (1 - decay_rate)
        self.pheromone_grid[self.pheromone_grid < 0.0001] = 0 # Clamp to 0

    def deposit_pheromone(self, x: int, y: int, amount: float):
        self.pheromone_grid[x, y] += amount
        self.pheromone_grid[self.pheromone_grid > 10.0] = 10.0 # Clamp max


    def remove_block_at(self, x: int, y: int) -> bool:
        block_coords = (x,y)
        if block_coords in self.blocks_pos and block_coords not in self.locked_blocks:
            self.blocks_pos.remove(block_coords)
            self.grid[x,y] = 0
            return True
        return False
        
    def place_block_at(self, x: int, y: int) -> bool:
        block_coords = (x,y)
        if self.grid[x,y] == 0 and block_coords not in self.locked_blocks and \
           block_coords != self.input_A and block_coords != self.input_B and \
           block_coords != self.join_point and block_coords != self.output_point:
            self.blocks_pos.append(block_coords)
            self.grid[x,y] = 1
            return True
        return False


# --- SIMULATION ---
def run_ant_colony_simulation() -> float:
    print(f"\n--- Simulation: Ant Colony Builders (Pheromones) ---", flush=True)
    
    N_AGENTS = 10
    N_INITIAL_LOOSE_BLOCKS = 30 # Number of blocks to start with, agents will move them
    
    blueprint_blocks = generate_wall_blueprint(GRID_SIZE, WALL_X)
    
    CYCLES = 3000 # More cycles for exploration
    VELOCITY_MAGNITUDE = 1.0 
    
    MAX_TEMPERATURE = 10.0 # Initial temperature for annealing

    # Environment Setup
    env = PheromoneEnvironment(GRID_SIZE, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT, num_initial_blocks=0)
    
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
            agent_id=f"ant_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    current_global_fitness = calculate_blueprint_fitness(env.blocks_pos, blueprint_blocks)
    print(f"Initial Fitness: {current_global_fitness:.2f}")
    
    for cycle in range(CYCLES):
        temperature = MAX_TEMPERATURE * (1 - cycle / CYCLES)
        
        env.unlock_blocks(cycle) # Unlock blocks
        env.evaporate_pheromones(PHEROMONE_DECAY) # Evaporate pheromones
        
        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent.state.position = np.array([agent_x, agent_y, 0.0])
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: pick up / drop / relocate
            
            # --- If not holding a block ---
            if not agent.holding_block_coords: 
                # Identify a potential block to pick up (prioritize clutter, then any block)
                potential_pickup_coords = None
                
                # Check current position first for clutter
                if env.grid[current_x, current_y] == 1 and (current_x, current_y) not in blueprint_blocks:
                    potential_pickup_coords = (current_x, current_y)
                
                # If not at current pos, scan neighbors for clutter
                if not potential_pickup_coords:
                    clutter_neighbors = []
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                        nx, ny = current_x + dx, current_y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and env.grid[nx,ny] == 1 and (nx,ny) not in blueprint_blocks:
                            clutter_neighbors.append((nx,ny))
                    if clutter_neighbors:
                        potential_pickup_coords = random.choice(clutter_neighbors)

                # If no clutter nearby, pick up any block (even from blueprint) for potential rearrangement
                if not potential_pickup_coords and env.blocks_pos:
                    potential_pickup_coords = random.choice(env.blocks_pos) 
                
                if potential_pickup_coords and potential_pickup_coords not in env.locked_blocks: # Only pickup if not locked
                    # Temporarily remove block and calculate fitness
                    block_x, block_y = potential_pickup_coords
                    
                    if env.remove_block_at(block_x, block_y): # This modifies env.blocks_pos and env.grid
                        temp_blocks_pos_after_pickup = list(env.blocks_pos)
                        test_fitness_after_pickup = calculate_blueprint_fitness(temp_blocks_pos_after_pickup, blueprint_blocks)
                        
                        # Decide whether to commit to pick up based on annealing
                        commit_pickup = False
                        if test_fitness_after_pickup > current_global_fitness:
                            commit_pickup = True
                        elif temperature > 0:
                            acceptance_probability = np.exp((test_fitness_after_pickup - current_global_fitness) / temperature)
                            if random.random() < acceptance_probability:
                                commit_pickup = True
                        
                        if commit_pickup:
                            agent.pick_up_from_grid(potential_pickup_coords) # Agent now holding it
                            current_global_fitness = test_fitness_after_pickup
                            env.locked_blocks[potential_pickup_coords] = cycle + LOCK_DURATION # Lock this removal
                        else: # Revert removal, block is still on the grid (logically)
                            env.place_block_at(block_x, block_y) # Put block back
            # --- If holding a block ---
            else: 
                # Scan neighbors for empty spots that are not locked
                candidate_spots = []
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                    nx, ny = current_x + dx, current_y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and env.grid[nx,ny] == 0 and \
                       (nx,ny) not in special_points and (nx,ny) not in env.locked_blocks:
                        candidate_spots.append((nx,ny))

                if candidate_spots:
                    # Choose a spot probabilistically based on pheromone and heuristic
                    spot_scores = []
                    for spot_coords in candidate_spots:
                        heuristic_score = 0.0
                        if spot_coords in blueprint_blocks: heuristic_score = 10.0 # High score for blueprint spot
                        
                        pheromone_score = env.pheromone_grid[spot_coords]
                        
                        spot_scores.append((spot_coords, pheromone_score + heuristic_score + 1.0)) # +1 to avoid zero total score
                    
                    total_score = sum(s for _, s in spot_scores)
                    if total_score > 0:
                        pick_score = random.uniform(0, total_score)
                        chosen_spot = None
                        for spot, score in spot_scores:
                            pick_score -= score
                            if pick_score <= 0:
                                chosen_spot = spot
                                break
                    else: # If all scores are 0, pick randomly
                        chosen_spot = random.choice([s for s, _ in spot_scores])
                    
                    if chosen_spot:
                        drop_x, drop_y = chosen_spot
                        
                        # Temporarily place block
                        if env.place_block_at(drop_x, drop_y): # This modifies env.blocks_pos and env.grid
                            temp_blocks_pos_after_placement = list(env.blocks_pos)
                            test_fitness_after_placement = calculate_blueprint_fitness(temp_blocks_pos_after_placement, blueprint_blocks)
                            
                            commit_placement = False
                            if test_fitness_after_placement > current_global_fitness:
                                commit_placement = True
                            elif temperature > 0:
                                acceptance_probability = np.exp((test_fitness_after_placement - current_global_fitness) / temperature)
                                if random.random() < acceptance_probability:
                                    commit_placement = True
                                    
                            if commit_placement:
                                agent.drop_on_grid()
                                current_global_fitness = test_fitness_after_placement
                                env.locked_blocks[chosen_spot] = cycle + LOCK_DURATION # Lock this placement
                                env.deposit_pheromone(drop_x, drop_y, PHEROMONE_DEPOSIT) # Deposit pheromone
                            else: # Revert, but might deposit negative pheromone?
                                env.remove_block_at(drop_x, drop_y) # Undo temporary place
                                env.deposit_pheromone(drop_x, drop_y, -PHEROMONE_DEPOSIT * 0.5) # Negative pheromone for bad move
                        
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
    final_fitness = run_ant_colony_simulation()
    if final_fitness >= len(generate_wall_blueprint(GRID_SIZE, WALL_X)) * 0.95: # Allow very minor clutter
        print("SUCCESS: Swarm constructed the wall according to blueprint.")
    else:
        print("FAILURE: Swarm failed to construct the wall.")
