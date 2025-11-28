import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

def apply_phase_noise(agent: FractalAgent, noise_strength: float):
    """Apply random phase noise to an agent."""
    noise = np.random.normal(0, noise_strength)
    agent.state.phase = (agent.state.phase + noise) % (2 * np.pi)

def create_cluster(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float) -> Tuple[List[FractalAgent], Dict[str, List[FractalAgent]]]:
    """Helper function to create agents and form a cluster."""
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen_{initial_phase}_{i}",
            energy=1.0,
            phase=initial_phase, 
            position=pos
        )
        agents.append(agent)

    # Move agents close
    center = np.array([50.0, 50.0, 0.0])
    for agent in agents:
        offset = np.random.rand(3) * 2.0
        agent.state.position = center + offset
        agent.state.phase = initial_phase + np.random.normal(0, 0.1) 
        
    clusters = comp_engine.compose_all(agents)
    
    cluster_map = {} 
    active_clusters = []
    
    for cluster in clusters:
        constituents = [a for a in agents if a.state.parent_id == cluster.state.agent_id]
        cluster_map[cluster.state.agent_id] = constituents
        active_clusters.append(cluster)
        
    return active_clusters, cluster_map

def run_experiment():
    print("MOG ONLINE: Cycle 1982 - Bit Flip Test", flush=True)
    print("Hypothesis: A cluster can be flipped from State 0 to State PI by applying an external signal exceeding a critical coupling threshold.", flush=True)
    
    # Parameters
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    NOISE_STRENGTH = 0.5
    COUPLING_K_INT = 0.1 # Internal glue
    
    # Sweep Parameters
    WRITE_STRENGTHS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
    WRITE_DURATION = 30 # cycles
    RELAX_DURATION = 50 # cycles to check stability
    TARGET_PHASE_0 = 0.0
    TARGET_PHASE_PI = np.pi

    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    results = {}

    for k_write in WRITE_STRENGTHS:
        print(f"\nTesting Write Strength K={k_write}...", flush=True)
        
        # 1. Init Cluster at 0
        clusters, cluster_map = create_cluster(N_AGENTS, WORLD_SIZE, comp_engine, TARGET_PHASE_0)
        if not clusters:
            print("  Failed to form cluster. Skipping.")
            continue
            
        cluster = clusters[0]
        constituents = cluster_map[cluster.state.agent_id]
        
        # 2. Run Simulation
        flip_successful = False
        phase_history = []
        
        for t in range(WRITE_DURATION + RELAX_DURATION):
            is_writing = t < WRITE_DURATION
            target = TARGET_PHASE_PI if is_writing else None # Removing target doesn't mean going back to 0, it means no external force
            
            # Internal Coupling (Restoring Force)
            # Cluster phase is mean of constituents
            sin_sum = sum(np.sin(c.state.phase) for c in constituents)
            cos_sum = sum(np.cos(c.state.phase) for c in constituents)
            mean_phase = np.arctan2(sin_sum, cos_sum)
            
            # Update constituents
            for child in constituents:
                # Internal force (pull to mean)
                f_int = COUPLING_K_INT * np.sin(mean_phase - child.state.phase)
                
                # External force (Write Signal) - only during write phase
                f_ext = 0.0
                if is_writing:
                    # Pull towards PI
                    f_ext = k_write * np.sin(TARGET_PHASE_PI - child.state.phase)
                
                child.state.phase += f_int + f_ext
                
                # Noise
                apply_phase_noise(child, NOISE_STRENGTH)
            
            # Update Cluster Phase
            sin_sum = sum(np.sin(c.state.phase) for c in constituents)
            cos_sum = sum(np.cos(c.state.phase) for c in constituents)
            avg_phase = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)
            cluster.state.phase = avg_phase
            
            phase_history.append(avg_phase)
            
        # 3. Evaluate
        # Check final average phase over last 10 steps
        final_phases = phase_history[-10:]
        # Circular mean of final phases
        final_sin = np.mean(np.sin(final_phases))
        final_cos = np.mean(np.cos(final_phases))
        final_avg = np.arctan2(final_sin, final_cos) % (2 * np.pi)
        
        # Distance from PI
        dist_pi = min(abs(final_avg - TARGET_PHASE_PI), 2*np.pi - abs(final_avg - TARGET_PHASE_PI))
        dist_0 = min(abs(final_avg - TARGET_PHASE_0), 2*np.pi - abs(final_avg - TARGET_PHASE_0))
        
        success = dist_pi < 1.0 # Arbitrary threshold, roughly pi/3
        
        print(f"  Final Phase: {final_avg:.4f} (Dist to PI: {dist_pi:.4f}, Dist to 0: {dist_0:.4f})")
        print(f"  Result: {'SUCCESS' if success else 'FAILURE'}")
        
        results[k_write] = {
            "success": success,
            "final_phase": final_avg,
            "dist_pi": dist_pi
        }

    # Analyze Critical Threshold
    print("\n--- Summary ---")
    threshold_found = False
    for k in WRITE_STRENGTHS:
        res = results[k]
        status = "FLIPPED" if res["success"] else "STUCK"
        print(f"K_write={k:.2f}: {status} (Final: {res['final_phase']:.2f})")
        
        if res["success"] and not threshold_found:
            print(f"CRITICAL THRESHOLD DETECTED between K={k-0.05:.2f} and K={k:.2f}")
            threshold_found = True

    if threshold_found:
        print("HYPOTHESIS CONFIRMED: Bit flip requires super-critical external forcing.")
    else:
        print("HYPOTHESIS FAILED: Could not flip bit (or flipped too easily).")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
