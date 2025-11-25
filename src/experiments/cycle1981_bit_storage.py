import sys
import os
import random
import numpy as np
import matplotlib.pyplot as plt
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

def create_cluster_and_singles(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float) -> Tuple[List[FractalAgent], List[FractalAgent], Dict[str, List[FractalAgent]]]:
    """Helper function to create agents, form a cluster, and return singles and cluster constituents."""
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen_{initial_phase}_{i}",
            energy=1.0,
            phase=initial_phase, # Set initial phase
            position=pos
        )
        agents.append(agent)

    # Separate agents into Control (Singles) and Experiment (Clusters)
    control_agents = agents[:N_AGENTS//2]
    experiment_agents = agents[N_AGENTS//2:]
    
    # Move experiment agents into groups of 10 to encourage distinct clusters
    for i, agent in enumerate(experiment_agents):
        group_idx = i // 10
        center = np.array([group_idx * 20.0, 20.0, 0.0]) # Spaced out
        offset = np.random.rand(3) * 2.0
        agent.state.position = center + offset
        agent.state.phase = initial_phase + np.random.normal(0, 0.1) # Align phases to allow composition
        
    # Only compose the experiment group
    clusters = comp_engine.compose_all(experiment_agents)
    
    # Re-map to find constituents
    cluster_map = {} # cluster_id -> list of constituent agents
    active_clusters = []
    
    for cluster in clusters:
        constituents = [a for a in agents if a.state.parent_id == cluster.state.agent_id]
        cluster_map[cluster.state.agent_id] = constituents
        active_clusters.append(cluster)
        
    print(f"  Formed {len(active_clusters)} Clusters from {len(experiment_agents)} Experiment Agents (Initial Phase: {initial_phase:.2f}).", flush=True)
    print(f"  Remaining Singles: {len(control_agents)}", flush=True)

    # Ensure all singles are set to the initial phase
    for s in control_agents:
        s.state.phase = initial_phase
        
    # Return active_clusters (parent agents) and cluster_map (constituents)
    return control_agents, active_clusters, cluster_map

def run_experiment():
    print("MOG ONLINE: Cycle 1981 - Bit Storage Test", flush=True)
    print("Hypothesis: Resonant Clusters can reliably store and differentiate discrete phase states (bits).", flush=True)
    
    # Parameters
    N_AGENTS = 200 # Total agents for each test (0 and pi)
    WORLD_SIZE = 100.0
    CYCLES = 200
    NOISE_STRENGTH = 0.5  # Radians
    COUPLING_K = 0.1 # Coupling Strength

    # We will test two scenarios: cluster initialized to 0 and cluster initialized to pi
    TARGET_PHASE_0 = 0.0
    TARGET_PHASE_PI = np.pi

    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)

    print("\n--- Testing Cluster initialized to 0.0 (BIT 0) ---", flush=True)
    singles_0, clusters_0, cluster_map_0 = create_cluster_and_singles(N_AGENTS, WORLD_SIZE, comp_engine, TARGET_PHASE_0)
    
    if not clusters_0:
        print("FAILURE: No clusters formed for BIT 0. Aborting.", flush=True)
        return

    print("\n--- Testing Cluster initialized to pi (BIT 1) ---", flush=True)
    singles_pi, clusters_pi, cluster_map_pi = create_cluster_and_singles(N_AGENTS, WORLD_SIZE, comp_engine, TARGET_PHASE_PI)
    
    if not clusters_pi:
        print("FAILURE: No clusters formed for BIT 1. Aborting.", flush=True)
        return

    # Initialize tracking
    history_single_0_error = []
    history_cluster_0_error = []
    history_single_pi_error = []
    history_cluster_pi_error = []

    print("\nStarting Noise Injection and Bit Differentiation Test...", flush=True)
    
    for t in range(CYCLES):
        # --- Process BIT 0 Cluster ---
        # 0. Apply Coupling (Resonance)
        for c in clusters_0:
            constituents = cluster_map_0[c.state.agent_id]
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            mean_phase = np.arctan2(sin_sum, cos_sum)
            for child in constituents:
                force = COUPLING_K * np.sin(mean_phase - child.state.phase)
                child.state.phase += force
        
        # 1. Apply Independent Noise to Base Agents
        for s in singles_0:
            apply_phase_noise(s, NOISE_STRENGTH)
        for c_parent in clusters_0:
            for child in cluster_map_0[c_parent.state.agent_id]:
                apply_phase_noise(child, NOISE_STRENGTH)
        
        # 2. Re-calculate Cluster Phase and Measure Error for BIT 0
        current_cluster_0_phases = []
        for c_parent in clusters_0:
            constituents = cluster_map_0[c_parent.state.agent_id]
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            avg_phase = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)
            c_parent.state.phase = avg_phase
            
            error = min(abs(avg_phase - TARGET_PHASE_0), 2*np.pi - abs(avg_phase - TARGET_PHASE_0))
            current_cluster_0_phases.append(error)
        history_cluster_0_error.append(np.mean(current_cluster_0_phases))

        current_single_0_phases = []
        for s in singles_0:
            error = min(abs(s.state.phase - TARGET_PHASE_0), 2*np.pi - abs(s.state.phase - TARGET_PHASE_0))
            current_single_0_phases.append(error)
        history_single_0_error.append(np.mean(current_single_0_phases))

        # --- Process BIT 1 Cluster ---
        # 0. Apply Coupling (Resonance)
        for c in clusters_pi:
            constituents = cluster_map_pi[c.state.agent_id]
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            mean_phase = np.arctan2(sin_sum, cos_sum)
            for child in constituents:
                force = COUPLING_K * np.sin(mean_phase - child.state.phase)
                child.state.phase += force
        
        # 1. Apply Independent Noise to Base Agents
        for s in singles_pi:
            apply_phase_noise(s, NOISE_STRENGTH)
        for c_parent in clusters_pi:
            for child in cluster_map_pi[c_parent.state.agent_id]:
                apply_phase_noise(child, NOISE_STRENGTH)
        
        # 2. Re-calculate Cluster Phase and Measure Error for BIT 1
        current_cluster_pi_phases = []
        for c_parent in clusters_pi:
            constituents = cluster_map_pi[c_parent.state.agent_id]
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            avg_phase = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)
            c_parent.state.phase = avg_phase
            
            # The "error" here is distance from TARGET_PHASE_PI
            error = min(abs(avg_phase - TARGET_PHASE_PI), 2*np.pi - abs(avg_phase - TARGET_PHASE_PI))
            current_cluster_pi_phases.append(error)
        history_cluster_pi_error.append(np.mean(current_cluster_pi_phases))

        current_single_pi_phases = []
        for s in singles_pi:
            error = min(abs(s.state.phase - TARGET_PHASE_PI), 2*np.pi - abs(s.state.phase - TARGET_PHASE_PI))
            current_single_pi_phases.append(error)
        history_single_pi_error.append(np.mean(current_single_pi_phases))

        if t % 20 == 0:
            print(f"Cycle {t}: Bit 0 (Avg Error Single/Cluster): {np.mean(current_single_0_phases):.4f}/{np.mean(current_cluster_0_phases):.4f} | Bit 1 (Avg Error Single/Cluster): {np.mean(current_single_pi_phases):.4f}/{np.mean(current_cluster_pi_phases):.4f}", flush=True)

    # Final Stats and Distinguishability Metric
    mean_single_0_error = np.mean(history_single_0_error)
    mean_cluster_0_error = np.mean(history_cluster_0_error)
    mean_single_pi_error = np.mean(history_single_pi_error)
    mean_cluster_pi_error = np.mean(history_cluster_pi_error)

    print("\n--- Final Results (N=200 cycles) ---")
    print(f"Average Bit 0 (Phase 0) Single Error: {mean_single_0_error:.4f}")
    print(f"Average Bit 0 (Phase 0) Cluster Error: {mean_cluster_0_error:.4f}")
    print(f"Average Bit 1 (Phase PI) Single Error: {mean_single_pi_error:.4f}")
    print(f"Average Bit 1 (Phase PI) Cluster Error: {mean_cluster_pi_error:.4f}")

    # Distinguishability: The "distance" between the mean phases of the two clusters
    # over time, normalized by their internal variance/error.
    # A bit is distinguishable if (avg_phase_pi - avg_phase_0) > (error_pi + error_0)
    
    # Calculate average final cluster phases
    final_avg_phase_0 = np.mean([c.state.phase for c in clusters_0])
    final_avg_phase_pi = np.mean([c.state.phase for c in clusters_pi])

    phase_distance = min(abs(final_avg_phase_pi - final_avg_phase_0), 2*np.pi - abs(final_avg_phase_pi - final_avg_phase_0))
    
    avg_cluster_error = (mean_cluster_0_error + mean_cluster_pi_error) / 2
    
    print(f"\nFinal Phase Distance between Bit 0 and Bit 1 Clusters: {phase_distance:.4f}")
    print(f"Average Cluster Error: {avg_cluster_error:.4f}")

    if phase_distance > 2 * avg_cluster_error: # Separation criterion
        print("SUCCESS: Discrete Bit Storage Confirmed. Clusters can reliably differentiate phase states.")
    else:
        print("FAILURE: Discrete Bit Storage Not Achieved. States are not reliably distinguishable.")

if __name__ == "__main__":
    from numpy import pi as np_pi # For type hint with numpy.pi
    run_experiment()
