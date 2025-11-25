
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2079_construction_physics import BuilderAgent

class OptimizerAgent(BuilderAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.holding_block = False
        
    def pick_up(self):
        if not self.holding_block:
            self.holding_block = True
            return True
        return False
    
    def drop(self):
        if self.holding_block:
            self.holding_block = False
            return True
        return False

def calculate_fitness(blocks: List[np.ndarray], target_radius: float, center: np.ndarray) -> float:
    if not blocks:
        return 0.0
    errors = []
    for pos in blocks:
        dist = np.linalg.norm(pos - center)
        error = abs(dist - target_radius)
        errors.append(error)
    return -sum(errors) # Higher is better (closer to 0 error)

def run_optimization_simulation() -> float:
    print(f"\n--- Simulation: Distributed Shape Optimization ---", flush=True)
    
    N_AGENTS = 50
    N_BLOCKS = 100 # Blocks available to move
    WORLD_SIZE = 100.0
    CENTER = np.array([50.0, 50.0, 0.0])
    TARGET_RADIUS = 20.0
    
    CYCLES = 1000
    VELOCITY_MAGNITUDE = 5.0
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = OptimizerAgent(
            agent_id=f"opt_{i}",
            energy=10.0, # High energy for logic test
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)
        
    # Initialize Blocks randomly
    blocks = []
    for _ in range(N_BLOCKS):
        blocks.append(np.random.rand(3) * WORLD_SIZE)
        blocks[-1][2] = 0
        
    current_fitness = calculate_fitness(blocks, TARGET_RADIUS, CENTER)
    initial_fitness = current_fitness
    print(f"Initial Fitness: {initial_fitness:.2f}")
    
    for cycle in range(CYCLES):
        # Agents move
        for agent in agents:
            # Random Walk
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE
            
            # Interaction with Blocks
            if agent.holding_block:
                # Maybe drop?
                # Annealing Logic: Try dropping. If fitness improves, leave it. Else pick up again.
                # But agent cannot "forecast". 
                # It must drop, measure local error?
                # Global fitness requires global knowledge.
                # Local Heuristic: Drop if |dist - target| is small.
                
                dist_to_center = np.linalg.norm(agent.state.position - CENTER)
                local_error = abs(dist_to_center - TARGET_RADIUS)
                
                if local_error < 2.0: # Good spot
                    agent.drop()
                    blocks.append(agent.state.position.copy())
            else:
                # Maybe pick up?
                # Check nearby blocks
                nearby_block_idx = -1
                for i, b_pos in enumerate(blocks):
                    if np.linalg.norm(agent.state.position - b_pos) < 2.0:
                        nearby_block_idx = i
                        break
                
                if nearby_block_idx != -1:
                    # Pick up if the block is in a "bad" spot
                    dist_to_center = np.linalg.norm(blocks[nearby_block_idx] - CENTER)
                    local_error = abs(dist_to_center - TARGET_RADIUS)
                    
                    if local_error > 5.0: # Bad spot
                        if agent.pick_up():
                            blocks.pop(nearby_block_idx)
                            
        if cycle % 100 == 0:
            current_fitness = calculate_fitness(blocks, TARGET_RADIUS, CENTER)
            print(f"Cycle {cycle}: Fitness {current_fitness:.2f}, Blocks Placed {len(blocks)}")
            
    final_fitness = calculate_fitness(blocks, TARGET_RADIUS, CENTER)
    improvement = final_fitness - initial_fitness
    print(f"Final Fitness: {final_fitness:.2f} (Improvement: {improvement:.2f})")
    
    return improvement

if __name__ == "__main__":
    imp = run_optimization_simulation()
    if imp > 100.0:
        print("SUCCESS: Swarm optimized the shape.")
    else:
        print("FAILURE: Swarm failed to optimize.")
