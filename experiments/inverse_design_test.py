"""
Helios v2: Inverse Design Experiment (Holographic Resilience)
Objective: Engineer a system that maintains N=100 despite 50% random deletion.
Method: Use TSF principles (Resonance + Pooling) to create a robust configuration.
"""

import sys
import os
import random
import numpy as np

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../code')))

from fractal.fractal_swarm import FractalSwarm
from core.reality_interface import RealityInterface

def run_inverse_design_test():
    print("--- HELIOS INVERSE DESIGN: HOLOGRAPHIC RESILIENCE ---")
    
    # 1. Configure System (Based on TSF Principles)
    # We use high coupling (Resonance) and energy sharing (Cooperation)
    # to create a "Holographic" state where information is distributed.
    config = {
        "agent_count": 100,
        "cycles": 500,
        "burst_threshold": 2000.0, # High threshold for criticality
        "enable_pooling": True,    # PRIN-COOPERATION
        "sharing_fraction": 0.2,
        "coupling_strength": 0.15  # PRIN-RESONANCE
    }
    
    print(f"Configuration: {config}")
    
    reality = RealityInterface()
    
    # 2. Initialize Swarm
    # Lower burst threshold to allow reproduction
    swarm = FractalSwarm(max_agents=200, burst_threshold=200.0) 
    
    for i in range(config["agent_count"]):
        swarm.spawn_agent(reality_metrics={}, initial_energy=100.0)
        
    print(f"Initial State: {len(swarm.agents)} agents")
    
    # 3. Run Simulation (Stabilization, Catastrophe, Recovery)
    print("Phase 1: Stabilization (Cycles 0-200)")
    
    recovery_history = [] # To track active agents for validation
    
    for cycle in range(config["cycles"]):
        # Apply Pooling
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        # print(f"DEBUG: Cycle {cycle}, Active Agents: {len(active_agents)}")
        if active_agents:
            swarm.energy_pooling_cycle(active_agents, sharing_fraction=config["sharing_fraction"])
            
        metrics = swarm.evolve_cycle(coupling_strength=config["coupling_strength"])
        recovery_history.append(metrics['active_agents']) # Track active agents per cycle
        
        # Debug energy
        if cycle % 10 == 0:
            avg_energy = metrics['total_energy'] / metrics['active_agents'] if metrics['active_agents'] > 0 else 0
            print(f"Cycle {cycle}: {metrics['active_agents']} agents, Avg Energy: {avg_energy:.2f}")

        if cycle == 200:
            print(f"State at Cycle 200: {metrics['active_agents']} active agents")
            if metrics['active_agents'] == 0:
                print("No active agents left before catastrophe. Exiting early.")
                break
            
            print("\n*** INJECTING CATASTROPHE: 50% DELETION ***")
            active_ids = [aid for aid, a in swarm.agents.items() if a.is_active]
            kill_count = int(len(active_ids) * 0.5)
            kill_ids = random.sample(active_ids, kill_count)
            
            for kid in kill_ids:
                # Manually kill
                swarm.agents[kid].energy = 0.0
                
            print(f"Killed {kill_count} agents. Remaining: {len([a for a in swarm.agents.values() if a.is_active])}")
            print("Phase 2: Recovery (Cycles 201-500)")
            
    # 6. Validate
    final_pop = recovery_history[-1] if recovery_history else 0
    recovery_rate = final_pop / config["agent_count"]
    print(f"\nFinal Population: {final_pop}")
    print(f"Recovery Rate: {recovery_rate:.2f}")
    
    if recovery_rate > 0.8:
        print("SUCCESS: System recovered to >80% capacity.")
        return True
    else:
        print("FAILURE: System failed to recover.")
        return False

if __name__ == "__main__":
    success = run_inverse_design_test()
    sys.exit(0 if success else 1)
