
import sys
import os
import random
import numpy as np
from typing import List, Dict, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent

# --- ENVIRONMENT & FLOW ---
class FlowEnvironment:
    def __init__(self, grid_size: int, input_points: List[Tuple[int, int]], output_point: Tuple[int, int], num_blocks: int):
        self.grid_size = grid_size
        self.input_points = input_points
        self.output_point = output_point
        self.num_blocks = num_blocks
        
        self.grid = np.zeros((grid_size, grid_size), dtype=int) # 0: empty, 1: block
        self.blocks_pos = [] # List of (x,y) tuples
        
        # Initialize blocks randomly
        for _ in range(num_blocks):
            x, y = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
            self.blocks_pos.append((x, y))
            self.grid[x, y] = 1
            
        # Ensure inputs/output are free
        for ip in input_points: self.grid[ip] = 0
        self.grid[output_point] = 0

    def place_block(self, x: int, y: int):
        if (x,y) not in self.input_points and (x,y) != self.output_point:
            if self.grid[x,y] == 0:
                self.grid[x,y] = 1
                self.blocks_pos.append((x,y))
                return True
        return False

    def remove_block(self, x: int, y: int):
        if self.grid[x,y] == 1:
            self.grid[x,y] = 0
            self.blocks_pos.remove((x,y))
            return True
        return False
        
    def simulate_flow(self, resource_input: float = 1.0, diffusion_rate: float = 0.5) -> float:
        potential = np.zeros((self.grid_size, self.grid_size))
        
        # Seed inputs
        for ix, iy in self.input_points:
            potential[ix, iy] = resource_input

        # Simulate diffusion
        for _ in range(10): # Iterations for diffusion to stabilize
            new_potential = np.copy(potential)
            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    if self.grid[x, y] == 1: # Blocked by a wall
                        new_potential[x, y] = 0
                        continue
                    
                    if (x,y) in self.input_points: # Input point maintains potential
                        new_potential[x,y] = resource_input
                        continue

                    # Diffuse from neighbors
                    avg_neighbor_potential = 0
                    num_neighbors = 0
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # 4-way connectivity
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx, ny] == 0:
                            avg_neighbor_potential += potential[nx, ny]
                            num_neighbors += 1
                    
                    if num_neighbors > 0:
                        # Update based on neighbors and current potential
                        new_potential[x,y] = (potential[x,y] * (1 - diffusion_rate)) + ((avg_neighbor_potential / num_neighbors) * diffusion_rate)
                    
            potential = new_potential
            
        return potential[self.output_point]

def run_combiner_simulation() -> float:
    print(f"\n--- Simulation: Analog Combiner Construction ---", flush=True)
    
    GRID_SIZE = 50 # Smaller grid for faster simulation
    N_AGENTS = 20
    N_BLOCKS = 50 # More blocks to form channels
    INPUT_POINTS = [(5, GRID_SIZE // 4), (5, (GRID_SIZE * 3) // 4)] # Two inputs on left
    OUTPUT_POINT = (GRID_SIZE - 5, GRID_SIZE // 2) # Single output on right
    
    CYCLES = 500
    VELOCITY_MAGNITUDE = 5.0
    
    # Environment Setup
    env = FlowEnvironment(GRID_SIZE, INPUT_POINTS, OUTPUT_POINT, N_BLOCKS)
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = OptimizerAgent(
            agent_id=f"builder_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    initial_flow = env.simulate_flow()
    print(f"Initial Output Flow: {initial_flow:.4f}")
    
    max_flow = initial_flow # Track best flow found
    
    for cycle in range(CYCLES):
        for agent in agents:
            # Move randomly (exploration)
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            
            # Ensure agent stays within grid boundaries
            agent_x = int((agent.state.position[0] + dx) % GRID_SIZE)
            agent_y = int((agent.state.position[1] + dy) % GRID_SIZE)
            agent.move(np.array([agent_x - agent.state.position[0], agent_y - agent.state.position[1], 0.0]))
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Try to pick up a block
            if not agent.holding_block and env.grid[current_x, current_y] == 1:
                if env.remove_block(current_x, current_y):
                    agent.pick_up()
                    
            # Try to drop a block
            if agent.holding_block and env.grid[current_x, current_y] == 0:
                # Evaluate potential move: if placing block here improves flow
                env.place_block(current_x, current_y)
                test_flow = env.simulate_flow()
                
                if test_flow > max_flow: # This is a good move! 
                    max_flow = test_flow
                    agent.drop() # Commit to the move
                else:
                    env.remove_block(current_x, current_y) # Revert bad move
        
        if cycle % 50 == 0:
            current_flow = env.simulate_flow()
            print(f"Cycle {cycle}: Max Flow {max_flow:.4f}, Current Flow {current_flow:.4f}")
            
    final_flow = env.simulate_flow()
    improvement = final_flow - initial_flow
    print(f"Final Output Flow: {final_flow:.4f} (Improvement: {improvement:.4f})")
    
    return improvement

if __name__ == "__main__":
    imp = run_combiner_simulation()
    if imp > 0.01: # Check for significant improvement
        print("SUCCESS: Swarm constructed an analog combiner.")
    else:
        print("FAILURE: Swarm failed to construct an effective combiner.")
