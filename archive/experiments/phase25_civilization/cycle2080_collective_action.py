
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2079_construction_physics import BuilderAgent, LedgerCompositionEngine

class StrategicBuilder(BuilderAgent):
    def __init__(self, strategy: str, **kwargs):
        super().__init__(**kwargs)
        self.strategy = strategy # 'Builder' or 'Freerider'
        
    def decide_build(self, cost: float) -> bool:
        if self.strategy == 'Freerider':
            return False
        return self.build(cost)

def run_valley_simulation(fraction_builders: float) -> Dict:
    print(f"\n--- Simulation: Builders {fraction_builders*100:.0f}% ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    CENTER = np.array([50.0, 50.0, 0.0])
    BUILD_RADIUS = 15.0 # Must be close to build
    
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
            energy=random.uniform(0.5, 1.0), # Initial buffer
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    history_height = []
    
    for cycle in range(CYCLES):
        # Determine current recharge rate
        current_recharge = RECHARGE_BASE
        if monument_height >= TOWER_THRESHOLD:
            current_recharge = REWARD_RECHARGE
            
        # 1. Movement & Building
        for agent in agents:
            # Builders want to go to center. Freeriders also go to center (to benefit? or just mimic?)
            # Let's say Freeriders hover near the shelter waiting for it to open.
            
            dist_to_center = np.linalg.norm(agent.state.position - CENTER)
            
            # Simple logic: Everyone goes to center to survive/build
            direction = CENTER - agent.state.position
            norm = np.linalg.norm(direction)
            if norm > 0:
                move_vec = (direction / norm) * VELOCITY_MAGNITUDE
                agent.move(move_vec)
            agent.state.position = agent.state.position % WORLD_SIZE
            
            # Build Logic
            if dist_to_center < BUILD_RADIUS:
                # Attempt build
                if agent.decide_build(BUILD_COST):
                    monument_height += 1
                    
        history_height.append(monument_height)

        # 2. Metabolism
        active_agents = []
        builders_alive = 0
        freeriders_alive = 0
        
        for agent in agents:
            agent.update_energy(current_recharge - METABOLIC_COST)
            if agent.state.energy > 0:
                active_agents.append(agent)
                if agent.strategy == 'Builder':
                    builders_alive += 1
                else:
                    freeriders_alive += 1
        
        agents = active_agents
        
        if not agents:
            # print(f"Cycle {cycle}: EXTINCTION.")
            break
            
    print(f"Final Height: {monument_height}")
    print(f"Survivors: {len(agents)} ({builders_alive} Builders, {freeriders_alive} Freeriders)")
    
    return {
        "height": monument_height,
        "survivors": len(agents),
        "builders": builders_alive,
        "freeriders": freeriders_alive,
        "success": monument_height >= TOWER_THRESHOLD
    }

def run_experiment():
    print("MOG ONLINE: Cycle 2080 - The Valley of Death", flush=True)
    
    # Scenario 1: 100% Builders
    res_100 = run_valley_simulation(1.0)
    
    # Scenario 2: 50% Builders
    res_50 = run_valley_simulation(0.5)
    
    # Scenario 3: 10% Builders
    res_10 = run_valley_simulation(0.1)
    
    print("\n--- ANALYSIS ---")
    print(f"100% Builders: {'Success' if res_100['success'] else 'Fail'} (H={res_100['height']})")
    print(f" 50% Builders: {'Success' if res_50['success'] else 'Fail'} (H={res_50['height']})")
    print(f" 10% Builders: {'Success' if res_10['success'] else 'Fail'} (H={res_10['height']})")

if __name__ == "__main__":
    run_experiment()
