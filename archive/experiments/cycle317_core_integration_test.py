"""
Cycle 317: Core Integration Test
Objective: Verify that FractalSwarm natively implements Asymmetric Mixed Coupling.
Hypothesis: A swarm spawned with default parameters (repulsive_fraction=0.3) should settle into the Complex Regime (0.3 < R < 0.7) when evolved with K > 0.
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fractal.fractal_swarm import FractalSwarm
from src.fractal.resonance import ResonanceDetector

def run_test():
    print("CYCLE 317: CORE INTEGRATION TEST")
    print("================================")
    
    # Parameters
    CYCLES = 100
    AGENTS = 50
    COUPLING_STRENGTH = 1.0 # Strong coupling, relying on frustration to prevent sync
    
    print(f"Initializing Swarm (Agents={AGENTS}, K={COUPLING_STRENGTH})")
    
    swarm = FractalSwarm(max_agents=AGENTS)
    
    # Spawn agents (will use default repulsive_fraction=0.3)
    for _ in range(AGENTS):
        swarm.spawn_agent(
            reality_metrics={}, 
            initial_energy=100.0, 
            phase=np.random.uniform(0, 2*np.pi)
        )
        
    # Verify Signs
    signs = [a.state.coupling_sign for a in swarm.agents.values()]
    pos_count = signs.count(1.0)
    neg_count = signs.count(-1.0)
    print(f"Distribution: {pos_count} Attractive (+), {neg_count} Repulsive (-)")
    
    detector = ResonanceDetector()
    order_parameters = []
    
    # Evolution Loop
    for t in range(CYCLES):
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        if not active_agents: break
        
        # Evolve using built-in logic (now includes Kuramoto force)
        swarm.evolve_cycle(coupling_strength=COUPLING_STRENGTH)
        
        # Measure Order
        coherence = detector.calculate_phase_coherence(active_agents)
        order_parameters.append(coherence)
        
    # Analyze Result
    mean_order = np.mean(order_parameters[-20:])
    print(f"Final Order Parameter (R): {mean_order:.4f}")
    
    # Save Results
    results = {
        "cycle": 317,
        "pos_count": pos_count,
        "neg_count": neg_count,
        "mean_order": mean_order,
        "trajectory": order_parameters
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/cycle317_core_integration.json", "w") as f:
        json.dump(results, f, indent=2)
        
    # Validation
    if 0.3 < mean_order < 0.7:
        print(f">> SUCCESS: System achieved Complex Regime (R={mean_order:.4f})")
    else:
        print(f">> FAILURE: System outside Complex Regime (R={mean_order:.4f})")

if __name__ == "__main__":
    run_test()
