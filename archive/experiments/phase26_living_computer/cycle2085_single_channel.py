
import sys
import os
import random
import numpy as np
from typing import List, Tuple, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2083_shape_optimization import OptimizerAgent

# --- ENVIRONMENT & CONNECTIVITY ---
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
        
    def has_path(self) -> bool:
        q = [(self.input_point[0], self.input_point[1])]
        visited = set()
        visited.add(self.input_point)

        while q:
            x, y = q.pop(0)
            if (x, y) == self.output_point:
                return True

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # 4-way connectivity
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and \
                   self.grid[nx, ny] == 0 and (nx, ny) not in visited: # Path goes through empty cells
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return False

    def get_block_at(self, x: int, y: int) -> Optional[Tuple[int,int]]:
        if self.grid[x,y] == 1:
            return (x,y)
        return None
        
    def remove_block_at(self, x: int, y: int) -> bool:
        if (x,y) in self.blocks_pos:
            self.blocks_pos.remove((x,y))
            self.grid[x,y] = 0
            return True
        return False
        
    def place_block_at(self, x: int, y: int) -> bool:
        if self.grid[x,y] == 0 and (x,y) not in self.input_point and (x,y) not in self.output_point:
            self.blocks_pos.append((x,y))
            self.grid[x,y] = 1
            return True
        return False


def run_channel_simulation() -> bool:
    print(f"\n--- Simulation: Single Channel Construction (Deconstruction) ---", flush=True)
    
    GRID_SIZE = 20 # Small grid for faster pathfinding
    N_AGENTS = 10
    N_INITIAL_BLOCKS = int(GRID_SIZE * GRID_SIZE * 0.4) # 40% filled randomly
    INPUT_POINT = (0, GRID_SIZE // 2)
    OUTPUT_POINT = (GRID_SIZE - 1, GRID_SIZE // 2)
    
    CYCLES = 500
    VELOCITY_MAGNITUDE = 1.0 # Slower movement in small grid
    
    # Environment Setup
    env = ConnectivityEnvironment(GRID_SIZE, INPUT_POINT, OUTPUT_POINT, N_INITIAL_BLOCKS)
    
    agents = []
    for i in range(N_AGENTS):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        agent = OptimizerAgent(
            agent_id=f"clearer_{i}",
            energy=10.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.array([x, y, 0.0])
        )
        agents.append(agent)
        
    initial_path_exists = env.has_path()
    print(f"Initial path exists: {initial_path_exists}")
    
    for cycle in range(CYCLES):
        if env.has_path():
            print(f"Cycle {cycle}: Path found!")
            return True # Success
            
        for agent in agents:
            # Move randomly
            agent_x = int((agent.state.position[0] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE)) % GRID_SIZE)
            agent_y = int((agent.state.position[1] + random.uniform(-VELOCITY_MAGNITUDE, VELOCITY_MAGNITUDE)) % GRID_SIZE)
            agent.move(np.array([agent_x - agent.state.position[0], agent_y - agent.state.position[1], 0.0]))
            
            current_x, current_y = int(agent.state.position[0]), int(agent.state.position[1])

            # Agent logic: If not holding a block, try to pick one up. If holding, try to drop it somewhere else.
            if not agent.holding_block:
                # Try to pick up a random block nearby, not necessarily at current pos
                target_block = random.choice(env.blocks_pos) if env.blocks_pos else None
                if target_block:
                    bx, by = target_block
                    # For simplicity, agent picks it up if it's "aware" of it, not just at current pos
                    # In a more complex sim, agent would move to block
                    if env.remove_block_at(bx, by):
                        agent.pick_up()
                        agent.state.position = np.array([bx, by, 0.0]) # Teleport to block
            else:
                # Try to drop the block at current position
                # Evaluate if dropping it here is good (i.e., doesn't block path)
                # But we want to CREATE path. So dropping means placing a block.
                # In this "Deconstruction" model, agent moves *empty space*.
                # Let's adjust: Agents remove blocks.
                
                # If holding a block, means it's an "obstacle" it removed.
                # It carries it around, trying to drop it in a non-critical spot.
                
                # For this experiment: Agents just remove blocks and try to create path.
                # Agent just tries to remove blocks.
                # If picking up made a path, it holds it.
                
                # Simplified: Agent attempts to remove a block. If removal creates path, it keeps it removed.
                # Else, it places it back and wanders.
                
                # To create a path: agent finds an empty spot and places a block (wall), hoping to guide
                # No, this is "clearing a path".
                
                # Let's say: Agent is holding a block (removed from grid). It tries to drop it in a *new* random empty spot.
                # If dropping it there (and thus clearing current pos) helps create a path, it does.
                # No, simpler logic:
                
                # Agent moves. If it's on a block, it picks it up. If after picking up, there's a path, it keeps holding.
                # If not, it puts it back.
                
                # This is still too complex for a first pass.
                
                # Simplest for C2085: Agents randomly remove blocks. Stop when path is found.
                # This is distributed random search for path clearance.
                
                # Agent behavior:
                # 1. Choose random location (x,y)
                # 2. If there's a block there, remove it.
                # 3. Check for path. If path, done.
                # 4. If not, maybe put it back (undo) if it didn't help.
                
                # Let's modify: Agent just picks up and drops blocks.
                # We need to test the effect of its *action*.
                
                # Let's simplify agent logic for this: Agent moves to a block, picks it up.
                # Checks if path exists. If yes, keeps it removed (block is gone).
                # If no, drops block back, tries another.
                
                # Find a block to remove
                if env.blocks_pos:
                    block_to_try_remove_idx = random.randrange(len(env.blocks_pos))
                    bx, by = env.blocks_pos[block_to_try_remove_idx]
                    
                    # Temporarily remove block
                    env.grid[bx, by] = 0
                    current_path_status = env.has_path()
                    env.grid[bx, by] = 1 # Put back
                    
                    if not current_path_status: # If no path yet
                        # If removing this block creates a path
                        env.grid[bx,by] = 0 # Actually remove
                        if env.has_path():
                            env.blocks_pos.pop(block_to_try_remove_idx) # Permanently removed
                            agent.holding_block = True # Agent holding block now (metaphorically)
                            print(f"Cycle {cycle}: Agent {agent.agent_id} removed block at ({bx},{by}) and found path!")
                            return True # Path found

                        env.grid[bx,by] = 1 # Put back, didn't help
                
        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Still searching for path...")
            
    final_path_exists = env.has_path()
    print(f"Final path exists: {final_path_exists}")
    
    return final_path_exists

if __name__ == "__main__":
    found_path = run_channel_simulation()
    if found_path:
        print("SUCCESS: Swarm cleared a connectivity channel.")
    else:
        print("FAILURE: Swarm failed to clear a channel.")
