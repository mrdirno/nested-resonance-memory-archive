
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2077_harsh_winter import GossipAgent, LedgerCompositionEngine

# --- BUILDER AGENT ---
class BuilderAgent(GossipAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blocks_built = 0
        
    def build(self, cost: float) -> bool:
        if self.state.energy > cost:
            self.state.energy -= cost
            self.blocks_built += 1
            return True
        return False

# --- CONSTRUCTION SIMULATION ---
def run_construction_simulation() -> int:
    print(f"\n--- Simulation: The First Monument ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    CENTER = np.array([50.0, 50.0, 0.0])
    BUILD_RADIUS = 10.0
    
    CYCLES = 200
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.05 # Abundant energy to allow building
    METABOLIC_COST = 0.01
    BUILD_COST = 0.20
    BUILD_THRESHOLD = 0.80 # Only build if rich
    
    # Monument State
    monument_height = 0
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = BuilderAgent(
            agent_id=f"builder_{i}",
            energy=random.uniform(0.5, 1.0),
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    # Composition Engine (Standard)
    comp_engine = LedgerCompositionEngine(distance_threshold=20.0, min_reputation=-0.1)
    cluster_registry = {} # Keep it simple for this physics test, mostly single agents building
    
    for cycle in range(CYCLES):
        # 1. Movement & Logic
        for agent in agents:
            # Logic: If rich, go to center to build. If poor, wander/recharge.
            dist_to_center = np.linalg.norm(agent.state.position - CENTER)
            
            if agent.state.energy > BUILD_THRESHOLD:
                # Go to center
                direction = CENTER - agent.state.position
                norm = np.linalg.norm(direction)
                if norm > 0:
                    move_vec = (direction / norm) * VELOCITY_MAGNITUDE
                    agent.move(move_vec)
            else:
                # Wander
                theta = random.uniform(0, 2*np.pi)
                dx = VELOCITY_MAGNITUDE * np.cos(theta)
                dy = VELOCITY_MAGNITUDE * np.sin(theta)
                agent.move(np.array([dx, dy, 0.0]))
            
            agent.state.position = agent.state.position % WORLD_SIZE
            
            # Build Check
            if dist_to_center < BUILD_RADIUS and agent.state.energy > BUILD_THRESHOLD:
                if agent.build(BUILD_COST):
                    monument_height += 1

        # 2. Metabolism
        active_agents = []
        for agent in agents:
            agent.update_energy(RECHARGE_RATE - METABOLIC_COST)
            if agent.state.energy > 0:
                active_agents.append(agent)
        agents = active_agents
        
        if cycle % 50 == 0:
            print(f"Cycle {cycle}: Tower Height = {monument_height}, Agents = {len(agents)}")
            
    print(f"Final Tower Height: {monument_height}")
    return monument_height

if __name__ == "__main__":
    height = run_construction_simulation()
    if height > 0:
        print("SUCCESS: Construction Physics Validated.")
    else:
        print("FAILURE: No construction occurred.")
