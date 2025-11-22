"""
Cycle 316: Repulsive Coupling (Breaking Rigid Order)
Objective: Implement repulsive coupling (negative K) to destabilize the rigid order attractor.
Hypothesis: Negative coupling will prevent global synchronization (R -> 1) and maintain the system in a complex regime (0.3 < R < 0.7).
"""

import sys
import os
import numpy as np
import json
import time
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.resonance import ResonanceDetector

def calculate_kuramoto_force(agents, coupling_strength):
    """
    Calculate the Kuramoto coupling force for each agent.
    F_i = (K / N) * sum(sin(phi_j - phi_i))
    """
    n = len(agents)
    if n == 0:
        return {}
        
    forces = {}
    phases = np.array([a.state.phase for a in agents])
    
    for i, agent in enumerate(agents):
        # Vectorized calculation of phase differences
        delta_phases = phases - agent.state.phase
        # Force contribution from each neighbor
        interactions = np.sin(delta_phases)
        # Average force
        force = (coupling_strength / n) * np.sum(interactions)
        forces[agent.agent_id] = force
        
    return forces

def run_experiment():
    print("CYCLE 316: REPULSIVE COUPLING EXPERIMENT (ITERATION 3)")
    print("======================================================")
    
    results = {}
    
    # Test 1: Fine-Grained Positive Sweep (The "Edge of Synchronization")
    print("\n--- Test 1: Fine-Grained Positive Sweep [0.01 - 0.05] ---")
    FINE_K = [0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05]
    CYCLES = 100
    AGENTS = 50
    
    for K in FINE_K:
        print(f"\nTesting Coupling Strength K = {K}")
        
        swarm = FractalSwarm(max_agents=AGENTS)
        for _ in range(AGENTS):
            swarm.spawn_agent(reality_metrics={}, initial_energy=100.0, phase=np.random.uniform(0, 2*np.pi))
            
        detector = ResonanceDetector()
        order_parameters = []
        
        for t in range(CYCLES):
            active_agents = [a for a in swarm.agents.values() if a.is_active]
            if not active_agents: break
            
            forces = calculate_kuramoto_force(active_agents, K)
            for agent in active_agents:
                agent.state.velocity = 0.1 + forces.get(agent.agent_id, 0.0)
            
            swarm.evolve_cycle(coupling_strength=0.0)
            order_parameters.append(detector.calculate_phase_coherence(active_agents))
            
        mean_order = np.mean(order_parameters[-20:])
        print(f"  Final Order Parameter (R): {mean_order:.4f}")
        results[f"Fine_K_{K}"] = mean_order

    # Test 2: Asymmetric Mixed Coupling (70% Attractive, 30% Repulsive)
    print("\n--- Test 2: Asymmetric Mixed Coupling (70/30) ---")
    MIXED_K_MAGNITUDES = [0.5, 1.0, 2.0]
    
    for K_mag in MIXED_K_MAGNITUDES:
        print(f"\nTesting Mixed Magnitude |K| = {K_mag}")
        
        swarm = FractalSwarm(max_agents=AGENTS)
        signs = np.ones(AGENTS)
        # Set last 30% to negative
        cutoff = int(AGENTS * 0.7)
        signs[cutoff:] = -1.0
        
        for i in range(AGENTS):
            agent = swarm.spawn_agent(reality_metrics={}, initial_energy=100.0, phase=np.random.uniform(0, 2*np.pi))
        
        agent_ids = list(swarm.agents.keys())
        sign_map = {aid: s for aid, s in zip(agent_ids, signs)}
            
        detector = ResonanceDetector()
        order_parameters = []
        
        for t in range(CYCLES):
            active_agents = [a for a in swarm.agents.values() if a.is_active]
            if not active_agents: break
            
            n = len(active_agents)
            phases = np.array([a.state.phase for a in active_agents])
            
            forces = {}
            for agent in active_agents:
                delta_phases = phases - agent.state.phase
                interactions = np.sin(delta_phases)
                k_i = sign_map[agent.agent_id] * K_mag
                force = (k_i / n) * np.sum(interactions)
                forces[agent.agent_id] = force
            
            for agent in active_agents:
                agent.state.velocity = 0.1 + forces.get(agent.agent_id, 0.0)
            
            swarm.evolve_cycle(coupling_strength=0.0)
            order_parameters.append(detector.calculate_phase_coherence(active_agents))
            
        mean_order = np.mean(order_parameters[-20:])
        print(f"  Final Order Parameter (R): {mean_order:.4f}")
        results[f"Asym_Mixed_K_{K_mag}"] = mean_order

    # Validation
    print("\nSUMMARY:")
    success = False
    for name, R in results.items():
        print(f"  {name:<15}: R={R:.4f}")
        if 0.3 < R < 0.7:
            print(f"  >> SUCCESS: {name} achieved Complex Regime (R={R:.4f})")
            success = True
            
    if not success:
        print("  >> FAILURE: No configuration achieved Complex Regime.")

if __name__ == "__main__":
    run_experiment()
