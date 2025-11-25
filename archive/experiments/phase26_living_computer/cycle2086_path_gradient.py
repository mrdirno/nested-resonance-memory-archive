
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Optional
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent

# --- ENVIRONMENT & CONNECTIVITY (REVISED) ---
class ConnectivityEnvironment:
    def __init__(self, grid_size: int, input_point: Tuple[int, int], output_point: Tuple[int, int], num_initial_blocks: int):
        self.grid_size = grid_size
        self.input_point = input_point
        self.output_point = output_point
        self.grid = np.zeros((grid_size, grid_size), dtype=int) # 0: empty, 1: block
        self.blocks_pos: List[Tuple[int,int]] = []

        # Seed initial blocks randomly, ensuring input/output are clear
        placed_count = 0
        while placed_count < num_initial_blocks:
            x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
            if (x,y) != input_point and (x,y) != output_point and self.grid[x,y] == 0:
                self.grid[x,y] = 1
                self.blocks_pos.append((x,y))
                placed_count += 1
        
    def get_shortest_path_length(self) -> float:
        q = deque([(self.input_point[0], self.input_point[1], 0)]) # (x, y, dist)
        visited = {self.input_point}

        while q:
            x, y, dist = q.popleft()
            if (x, y) == self.output_point:
                return float(dist)

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # 4-way connectivity
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and \
                   self.grid[nx, ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, dist + 1))
        return float('inf')

    def get_block_at(self, x: int, y: int) -> Optional[Tuple[int,int]]:
        if self.grid[x,y] == 1:
            return (x,y)
        return None
        
    def remove_block_at(self, x: int, y: int) -> bool:
        if (x,y) in self.blocks_pos: # Check by list membership for safety
            self.blocks_pos.remove((x,y))
            self.grid[x,y] = 0
            return True
        return False
        
    def place_block_at(self, x: int, y: int) -> bool:
        # Can only place in empty spots, not input/output
        if self.grid[x,y] == 0 and (x,y) not in self.input_point and (x,y) not in self.output_point:
            self.blocks_pos.append((x,y))
            self.grid[x,y] = 1
            return True
        return False


# --- SIMULATION ---
def run_gradient_simulation() -> bool:
    print(f"\n--- Simulation: Gradient of Connectivity ---", flush=True)
    
    GRID_SIZE = 20 # Small grid for faster pathfinding
    N_AGENTS = 10
    N_INITIAL_BLOCKS = int(GRID_SIZE * GRID_SIZE * 0.4) # 40% filled randomly
    INPUT_POINT = (0, GRID_SIZE // 2)
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    CYCLES = 1000
    VELOCITY_MAGNITUDE = 1.0 # Slower movement in small grid
    
    # Environment Setup
    env = ConnectivityEnvironment(GRID_SIZE, INPUT_POINT, OUTPUT_POINT, N_INITIAL_BLOCKS)
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = OptimizerAgent( # OptimizerAgent has .holding_block
            agent_id=f"clearer_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    initial_path_length = env.get_shortest_path_length()
    print(f"Initial Path Length: {initial_path_length}")
    
    for cycle in range(CYCLES):
        current_global_path_length = env.get_shortest_path_length()
        if current_global_path_length != float('inf'):
            print(f"Cycle {cycle}: Path found with length {current_global_path_length}!")
            return True # Success

        for agent in agents:
            # Random movement
            agent_x = int(max(0, min(GRID_SIZE-1, agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent_y = int(max(0, min(GRID_SIZE-1, agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE))))
            agent.move(np.array([agent_x - agent.state.position[0], agent_y - agent.state.position[1], 0.0]))
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: Try to improve path length
            if not agent.holding_block:
                # Agent is empty-handed, tries to remove a block if it's currently on one
                if env.grid[current_x, current_y] == 1:
                    env.grid[current_x, current_y] = 0 # Temporarily remove
                    test_path_length = env.get_shortest_path_length()
                    
                    if test_path_length < current_global_path_length: # If removing this block shortens path (improves fitness)
                        # Commit to removal
                        if env.remove_block_at(current_x, current_y): # This also updates blocks_pos
                            agent.pick_up()
                            # print(f"Agent {agent.agent_id} removed block at ({current_x},{current_y}). New path length: {test_path_length}")
                            current_global_path_length = test_path_length
                    else:
                        env.grid[current_x, current_y] = 1 # Put block back, it didn't help
            else:
                # Agent is holding a block, tries to place it
                # Agent tries to drop block in a random empty adjacent spot that does not increase path length
                possible_drop_spots = []
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]: # 8 neighbors
                    nx, ny = current_x + dx, current_y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and env.grid[nx,ny] == 0:
                         if (nx,ny) != env.input_point and (nx,ny) != env.output_point:
                            possible_drop_spots.append((nx,ny))

                if possible_drop_spots:
                    drop_x, drop_y = random.choice(possible_drop_spots)
                    env.grid[drop_x, drop_y] = 1 # Temporarily place block
                    test_path_length = env.get_shortest_path_length()
                    
                    if test_path_length <= current_global_path_length: # If placing doesn't worsen path
                        # Commit to placement
                        if env.place_block_at(drop_x, drop_y): # This also updates blocks_pos
                            agent.drop()
                            # print(f"Agent {agent.agent_id} placed block at ({drop_x},{drop_y}). Path length: {test_path_length}")
                            current_global_path_length = test_path_length
                    else:
                        env.grid[drop_x, drop_y] = 0 # Remove block, it worsened path
                
        # Small chance to randomly pick up/drop if stuck in local minima
        if random.random() < 0.01:
            if env.blocks_pos and not agent.holding_block:
                bx, by = random.choice(env.blocks_pos)
                if env.remove_block_at(bx,by): agent.pick_up()
            elif agent.holding_block:
                ex, ey = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                if env.place_block_at(ex,ey): agent.drop()


        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Current Path Length = {current_global_path_length}")
            
    final_path_length = env.get_shortest_path_length()
    print(f"Final Path Length: {final_path_length}")
    
    return final_path_length != float('inf')

if __name__ == "__main__":
    found_path = run_gradient_simulation()
    if found_path:
        print("SUCCESS: Swarm cleared a connectivity channel.")
    else:
        print("FAILURE: Swarm failed to clear a channel.")
