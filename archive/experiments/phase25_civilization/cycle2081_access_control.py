
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2080_collective_action import StrategicBuilder

def run_club_simulation(fraction_builders: float, access_control: bool) -> Dict:
    print(f"\n--- Simulation: Builders {fraction_builders*100:.0f}%, Access Control {'ON' if access_control else 'OFF'} ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    CENTER = np.array([50.0, 50.0, 0.0])
    BUILD_RADIUS = 15.0
    
    CYCLES = 300
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_BASE = 0.02
    METABOLIC_COST = 0.03 # Net -0.01 (Death)
    
    BUILD_COST = 0.10
    TOWER_THRESHOLD = 100
    REWARD_RECHARGE = 0.05 # Net +0.02 (Survival)
    
    monument_height = 0
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        strat = 'Builder' if i < N_AGENTS * fraction_builders else 'Freerider'
        agent = StrategicBuilder(
            strategy=strat,
            agent_id=f"gen0_{i}",
            energy=random.uniform(0.5, 1.0), 
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)
    
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
                    
        # 2. Metabolism & Rewards
        active_agents = []
        builders_alive = 0
        freeriders_alive = 0
        
        for agent in agents:
            # Determine individual recharge
            recharge = RECHARGE_BASE
            
            if monument_height >= TOWER_THRESHOLD:
                if access_control:
                    # Only contributors get access
                    if agent.blocks_built > 0:
                        recharge = REWARD_RECHARGE
                    else:
                        recharge = RECHARGE_BASE # Freeriders locked out
                else:
                    # Public Good (Everyone gets it)
                    recharge = REWARD_RECHARGE
            
            agent.update_energy(recharge - METABOLIC_COST)
            
            if agent.state.energy > 0:
                active_agents.append(agent)
                if agent.strategy == 'Builder':
                    builders_alive += 1
                else:
                    freeriders_alive += 1
        
        agents = active_agents
        
        if not agents:
            break
            
    print(f"Final Height: {monument_height}")
    print(f"Survivors: {len(agents)} ({builders_alive} Builders, {freeriders_alive} Freeriders)")
    
    return {
        "builders": builders_alive,
        "freeriders": freeriders_alive
    }

def run_experiment():
    print("MOG ONLINE: Cycle 2081 - The Club Good", flush=True)
    
    # Control: 50% Builders, No Access Control
    res_control = run_club_simulation(0.5, access_control=False)
    
    # Treatment: 50% Builders, Access Control ON
    res_treatment = run_club_simulation(0.5, access_control=True)
    
    if res_treatment['builders'] > 0 and res_treatment['freeriders'] == 0:
        print("\nSUCCESS: Access Control eliminated Freeriders.")
    else:
        print("\nFAILURE: Freeriders survived or Builders died.")

if __name__ == "__main__":
    run_experiment()
