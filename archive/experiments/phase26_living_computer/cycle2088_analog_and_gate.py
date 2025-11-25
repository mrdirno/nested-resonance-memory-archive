
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Optional
from collections import deque

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent
from src.experiments.cycle2087_exploratory_excavators import ConnectivityEnvironment # Reuse base env for pathfinding

# --- ENVIRONMENT FOR AND GATE ---
class AndGateEnvironment(ConnectivityEnvironment):
    def __init__(self, grid_size: int, input_A: Tuple[int, int], input_B: Tuple[int, int], join_point: Tuple[int, int], output_point: Tuple[int, int], num_initial_blocks: int = 0):
        # Initialize with an empty grid, blocks are placed later
        super().__init__(grid_size, input_A, output_point, num_initial_blocks) 
        
        self.input_A = input_A
        self.input_B = input_B
        self.join_point = join_point
        self.output_point = output_point
        
        # Ensure input/output/join points are always clear
        self.grid[input_A] = 0
        self.grid[input_B] = 0
        self.grid[join_point] = 0
        self.grid[output_point] = 0
        
        # Clear blocks_pos inherited from super, since grid starts empty
        self.blocks_pos = []

    def calculate_and_fitness(self) -> float:
        score = 0.0
        
        # Path A to Join Point
        if self._has_path_internal(self.input_A, self.join_point): score += 1.0
        # Path B to Join Point
        if self._has_path_internal(self.input_B, self.join_point): score += 1.0
        # Path Join Point to Output
        if self._has_path_internal(self.join_point, self.output_point): score += 1.0
        
        # Penalty for direct A-B path (Inputs should be isolated until the join point)
        if self._has_path_internal(self.input_A, self.input_B): score -= 1.0 
        
        return score

    def _has_path_internal(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        q = deque([(start[0], start[1])])
        visited = {start}

        while q:
            x, y = q.popleft()
            if (x, y) == end:
                return True

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # 4-way connectivity
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and \
                   self.grid[nx, ny] == 0 and (nx, ny) not in visited: # Path goes through empty cells
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return False
        
    def place_block_at(self, x: int, y: int) -> bool:
        # Can only place in empty spots, not input/output/join points
        if self.grid[x,y] == 0 and \
           (x,y) != self.input_A and (x,y) != self.input_B and \
           (x,y) != self.join_point and (x,y) != self.output_point:
            self.blocks_pos.append((x,y))
            self.grid[x,y] = 1
            return True
        return False


# --- SIMULATION ---
def run_and_gate_simulation() -> float:
    print(f"\n--- Simulation: Analog AND Gate Construction ---", flush=True)
    
    GRID_SIZE = 20 
    N_AGENTS = 10
    
    INPUT_A = (0, 5)
    INPUT_B = (0, 14)
    JOIN_POINT = (GRID_SIZE // 2, GRID_SIZE // 2) # Center
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    CYCLES = 1000
    VELOCITY_MAGNITUDE = 1.0 
    
    # Environment Setup: Start empty
    env = AndGateEnvironment(GRID_SIZE, INPUT_A, INPUT_B, JOIN_POINT, OUTPUT_POINT, num_initial_blocks=0)
    
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
        
    current_global_fitness = env.calculate_and_fitness()
    initial_fitness = current_global_fitness
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
                   (current_x, current_y) != env.input_A and (current_x, current_y) != env.input_B and \
                   (current_x, current_y) != env.join_point and (current_x, current_y) != env.output_point:
                    
                    env.grid[current_x, current_y] = 1 # Temporarily place block
                    test_fitness = env.calculate_and_fitness()
                    
                    if test_fitness > current_global_fitness: # If placing improves fitness
                        # Commit to placement
                        if env.place_block_at(current_x, current_y): # This also updates blocks_pos
                            agent.drop() # Agent successfully placed block
                            agent.holding_block = True # Get a new block instantly from supply (infinite)
                            current_global_fitness = test_fitness
                            # print(f"Agent {agent.agent_id} placed block at ({current_x},{current_y}). Fitness: {test_fitness}")
                    else:
                        env.grid[current_x, current_y] = 0 # Remove block, it didn't help
                
        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Current Fitness = {current_global_fitness:.2f}")
            
        if current_global_fitness >= 3.0: # Ideal fitness is 3.0 (A->J, B->J, J->O, no A->B)
            print(f"Cycle {cycle}: AND Gate achieved! Fitness = {current_global_fitness:.2f}")
            break
            
    final_fitness = env.calculate_and_fitness()
    print(f"Final Fitness: {final_fitness:.2f}")
    
    return final_fitness

if __name__ == "__main__":
    final_fitness = run_and_gate_simulation()
    if final_fitness >= 3.0:
        print("SUCCESS: Swarm constructed a functional Analog AND Gate.")
    else:
        print("FAILURE: Swarm failed to construct an effective Analog AND Gate.")
