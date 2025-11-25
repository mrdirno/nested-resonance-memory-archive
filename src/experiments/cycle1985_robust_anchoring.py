import sys
import os
import random
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

def apply_phase_noise(agent: FractalAgent, noise_strength: float):
    """Apply random phase noise to an agent."""
    noise = np.random.normal(0, noise_strength)
    agent.state.phase = (agent.state.phase + noise) % (2 * np.pi)

def phase_diff(p1, p2):
    """Calculate the shortest angular distance between two phases."""
    d = abs(p1 - p2)
    return min(d, 2 * np.pi - d)

def create_cluster(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float) -> Tuple[FractalAgent, List[FractalAgent]]:
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"anchor_{i}",
            energy=1.0,
            phase=initial_phase, 
            position=pos
        )
        agents.append(agent)

    # Force clustering
    center = np.array([50.0, 50.0, 0.0])
    for agent in agents:
        offset = np.random.rand(3) * 2.0
        agent.state.position = center + offset
        agent.state.phase = initial_phase + np.random.normal(0, 0.1) 
        
    clusters = comp_engine.compose_all(agents)
    if not clusters:
        # Fallback: if composition fails (unlikely with high params), just return list
        # This is a mock cluster for testing if comp engine is strict
        return None, agents # Should be handled by caller

    parent = clusters[0]
    constituents = [a for a in agents if a.state.parent_id == parent.state.agent_id]
    return parent, constituents

def run_experiment():
    print("MOG ONLINE: Cycle 1985 - Robust Phase Anchoring", flush=True)
    print("Objective: Compare driving functions to find a mechanism that anchors phase to 0.0 despite high noise.", flush=True)
    
    # Parameters
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    NOISE_STRENGTH = 0.5 # High noise that broke Cycle 1984
    COUPLING_K_INT = 0.1 # Standard internal coupling
    DRIVE_STRENGTH_K = 0.2 # Moderate drive strength
    CYCLES = 300
    TARGET_PHASE = 0.0
    
    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    # Strategies to test
    strategies = {
        "Linear (Sine)": lambda err, k: k * np.sin(err),
        "Sigmoidal (Tanh)": lambda err, k: k * np.tanh(5.0 * np.sin(err)), # High gain near 0
        "Bang-Bang (Sign)": lambda err, k: k * np.sign(np.sin(err)),
        "Cubic": lambda err, k: k * (np.sin(err))**3,
    }
    
    results = {}
    
    for name, force_func in strategies.items():
        print(f"\nTesting Strategy: {name}", flush=True)
        
        # Setup Cluster
        parent, constituents = create_cluster(N_AGENTS, WORLD_SIZE, comp_engine, TARGET_PHASE)
        if not parent:
            print("Failed to form cluster. Skipping.")
            continue
            
        # Shift cluster slightly off target to test pull-in
        initial_offset = 0.5
        for c in constituents:
            c.state.phase = (TARGET_PHASE + initial_offset) % (2 * np.pi)
            
        # Simulation
        errors = []
        
        for t in range(CYCLES):
            # Calc Mean Phase
            sin_sum = sum(np.sin(c.state.phase) for c in constituents)
            cos_sum = sum(np.cos(c.state.phase) for c in constituents)
            mean_phase = np.arctan2(sin_sum, cos_sum)
            
            # Apply Forces
            for child in constituents:
                # 1. Internal Coupling (Cohesion)
                f_int = COUPLING_K_INT * np.sin(mean_phase - child.state.phase)
                
                # 2. Anchoring Drive (External Force)
                # err = target - current
                err = TARGET_PHASE - child.state.phase
                f_ext = force_func(err, DRIVE_STRENGTH_K)
                
                child.state.phase += f_int + f_ext
                apply_phase_noise(child, NOISE_STRENGTH)
                
            # Measure Cluster Error
            sin_sum = sum(np.sin(c.state.phase) for c in constituents)
            cos_sum = sum(np.cos(c.state.phase) for c in constituents)
            current_mean = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)
            
            dist = phase_diff(current_mean, TARGET_PHASE)
            errors.append(dist)
            
        avg_error = np.mean(errors[-50:]) # Last 50 steps
        std_error = np.std(errors[-50:])
        print(f"  Final Avg Error: {avg_error:.4f} (Std: {std_error:.4f})")
        results[name] = avg_error

    print("\n--- Summary ---")
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    for name, err in sorted_results:
        print(f"{name}: {err:.4f}")
        
    best_strategy = sorted_results[0][0]
    best_err = sorted_results[0][1]
    
    if best_err < 0.2:
        print(f"\nSUCCESS: {best_strategy} provides robust anchoring (Error < 0.2).")
    else:
        print(f"\nFAILURE: Even best strategy ({best_strategy}) failed to hold error < 0.2 under noise {NOISE_STRENGTH}.")

if __name__ == "__main__":
    run_experiment()
