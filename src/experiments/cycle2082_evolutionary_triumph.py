import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2080_collective_action import StrategicBuilder

def run_evolution_simulation() -> float:
    print(f"\n--- Simulation: Evolutionary Triumph (Access Control ON) ---", flush=True)
    
    N_INITIAL = 50
    MAX_AGENTS = 200
    WORLD_SIZE = 100.0
    CENTER = np.array([50.0, 50.0, 0.0])
    BUILD_RADIUS = 15.0
    
    CYCLES = 1000
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_BASE = 0.02
    METABOLIC_COST = 0.03
    
    BUILD_COST = 0.10
    TOWER_THRESHOLD = 100
    REWARD_RECHARGE = 0.06 # Net +0.03 (Fast growth)
    
    monument_height = 0
    
    agents = []
    # Initial: 50% Builders
    for i in range(N_INITIAL):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        strat = 'Builder' if i < N_INITIAL // 2 else 'Freerider'
        agent = StrategicBuilder(
            strategy=strat,
            agent_id=f"gen0_{i}",
            energy=random.uniform(0.5, 1.0), 
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)
    
    builder_fraction_history = []
    
    for cycle in range(CYCLES):
        # 1. Movement & Building
        for agent in agents:
            dist_to_center = np.linalg.norm(agent.state.position - CENTER)
            direction = CENTER - agent.state.position
            norm = np.linalg.norm(direction)
            if norm > 0:
                move_vec = (direction / norm) * VELOCITY_MAGNITUDE
                agent.move(move_vec)
            agent.state.position = agent.state.position % WORLD_SIZE
            
            if dist_to_center < BUILD_RADIUS:
                if agent.decide_build(BUILD_COST):
                    monument_height += 1
                    
        # 2. Metabolism, Rewards, Reproduction
        active_agents = []
        new_agents = []
        
        builders_count = 0
        freeriders_count = 0
        
        for agent in agents:
            # Reward Logic (Access Control ON)
            recharge = RECHARGE_BASE
            if monument_height >= TOWER_THRESHOLD:
                if agent.blocks_built > 0:
                    recharge = REWARD_RECHARGE
                else:
                    recharge = RECHARGE_BASE
            
            agent.update_energy(recharge - METABOLIC_COST)
            
            if agent.state.energy > 0:
                active_agents.append(agent)
                if agent.strategy == 'Builder':
                    builders_count += 1
                else:
                    freeriders_count += 1
                    
                # Reproduction
                if agent.state.energy > 1.5 and (len(agents) + len(new_agents)) < MAX_AGENTS:
                    agent.state.energy *= 0.5
                    child = StrategicBuilder(
                        strategy=agent.strategy, # Inherit strategy
                        agent_id=f"child_{cycle}_{len(new_agents)}",
                        energy=agent.state.energy,
                        phase=agent.state.phase, # Inherit phase
                        position=agent.state.position + np.random.rand(3) # Nearby
                    )
                    # IMPORTANT: Child inherits 0 blocks built. Must earn their keep!
                    new_agents.append(child)

        agents = active_agents + new_agents
        
        total = len(agents)
        if total > 0:
            frac = builders_count / total
            builder_fraction_history.append(frac)
        else:
            break
            
        if cycle % 100 == 0:
            print(f"Cycle {cycle}: Pop {total} ({builders_count} B, {freeriders_count} F), Tower {monument_height}")
            
        if freeriders_count == 0 and builders_count > 10:
            print(f"Cycle {cycle}: FREERIDERS EXTINCT.")
            break

    final_frac = builder_fraction_history[-1] if builder_fraction_history else 0.0
    print(f"Final Builder Fraction: {final_frac:.2f}")
    return final_frac

if __name__ == "__main__":
    final_frac = run_evolution_simulation()
    if final_frac > 0.95:
        print("SUCCESS: Builders dominated the population.")
    else:
        print("FAILURE: Builders did not dominate.")
