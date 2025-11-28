import sys
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Set
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

def apply_phase_noise(agent: FractalAgent, noise_strength: float):
    """Apply random phase noise to an agent."""
    noise = np.random.normal(0, noise_strength)
    agent.state.phase = (agent.state.phase + noise) % (2 * np.pi)

def run_experiment():
    print("MOG ONLINE: Cycle 1980 - Phase Memory Test", flush=True)
    print("Hypothesis: Clusters (Ensembles) exhibit higher phase stability (Memory) than Single Agents due to statistical averaging (CLT).", flush=True)
    
    # Parameters
    N_AGENTS = 200
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 200
    NOISE_STRENGTH = 0.5  # Radians
    
    # Setup
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    # Separate agents into Control (Singles) and Experiment (Clusters)
    control_agents = agents[:N_AGENTS//2]
    experiment_agents = agents[N_AGENTS//2:]
    
    # Force Cluster Formation (High Resonance, High Willingness)
    print("Initializing Clusters...", flush=True)
    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    # Move experiment agents into groups of 10 to encourage distinct clusters
    for i, agent in enumerate(experiment_agents):
        group_idx = i // 10
        center = np.array([group_idx * 20.0, 20.0, 0.0]) # Spaced out
        offset = np.random.rand(3) * 2.0
        agent.state.position = center + offset
        agent.state.phase = 0.0 + np.random.normal(0, 0.1)
        
    # Only compose the experiment group
    clusters = comp_engine.compose_all(experiment_agents)
    
    # Control group remains as singles
    singles = control_agents
    # Constituents are effectively hidden in the composition engine logic, 
    # but we want to simulate them.
    # The 'clusters' list contains the new parent agents.
    # We need to track the *constituents* of these clusters.
    
    # Re-map to find constituents
    cluster_map = {} # cluster_id -> list of constituent agents
    active_clusters = []
    
    # Since compose_all returns NEW agents and modifies old ones (setting parent_id)
    # We need to check which 'agents' became constituents
    
    for cluster in clusters:
        constituents = [a for a in agents if a.state.parent_id == cluster.state.agent_id]
        cluster_map[cluster.state.agent_id] = constituents
        active_clusters.append(cluster)
        
    print(f"Formed {len(active_clusters)} Clusters from {len(agents)} Agents.", flush=True)
    print(f"Remaining Singles: {len(singles)}", flush=True)
    
    if len(active_clusters) == 0:
        print("FAILURE: No clusters formed. Aborting.", flush=True)
        return

    # Tracking
    history_single_variance = []
    history_cluster_variance = []
    
    # Target Phase (Memory)
    TARGET_PHASE = 0.0
    
    # Initialize all to Target Phase
    for s in singles:
        s.state.phase = TARGET_PHASE
    for c in active_clusters:
        c.state.phase = TARGET_PHASE # Cluster phase
        for child in cluster_map[c.state.agent_id]:
            child.state.phase = TARGET_PHASE

    # Coupling Strength
    COUPLING_K = 0.1

    print("Starting Noise Injection...", flush=True)
    
    for t in range(CYCLES):
        # 0. Apply Coupling (Resonance) - The "Structure" Force
        # This keeps the cluster constituents synchronized so the "Cluster Phase" remains valid.
        for c in active_clusters:
            constituents = cluster_map[c.state.agent_id]
            # Calculate Order Parameter (Mean Field)
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            mean_phase = np.arctan2(sin_sum, cos_sum)
            
            # Pull towards mean
            for child in constituents:
                # d_phi = K * sin(mean - phi)
                force = COUPLING_K * np.sin(mean_phase - child.state.phase)
                child.state.phase += force

        # 1. Apply Independent Noise to ALL Base Agents (Singles + Constituents)
        # The environment is noisy.
        
        # Noise for Singles
        single_phases = []
        for s in singles:
            apply_phase_noise(s, NOISE_STRENGTH)
            diff = min(abs(s.state.phase - TARGET_PHASE), 2*np.pi - abs(s.state.phase - TARGET_PHASE))
            single_phases.append(diff)
            
        # Noise for Constituents (which drives Cluster Phase)
        cluster_phases = []
        for c in active_clusters:
            constituents = cluster_map[c.state.agent_id]
            for child in constituents:
                apply_phase_noise(child, NOISE_STRENGTH)
            
            # Re-calculate Cluster Phase (Ensemble Average)
            # We assume the cluster phase is the vector average of constituents
            # Sum of sin/cos to handle periodicity correctly
            sin_sum = sum(np.sin(child.state.phase) for child in constituents)
            cos_sum = sum(np.cos(child.state.phase) for child in constituents)
            avg_phase = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)
            
            c.state.phase = avg_phase
            
            diff = min(abs(c.state.phase - TARGET_PHASE), 2*np.pi - abs(c.state.phase - TARGET_PHASE))
            cluster_phases.append(diff)
            
        # 2. Measure Variance/Error
        var_single = np.mean(single_phases) if single_phases else 0.0
        var_cluster = np.mean(cluster_phases) if cluster_phases else 0.0
        
        history_single_variance.append(var_single)
        history_cluster_variance.append(var_cluster)
        
        if t % 20 == 0:
            print(f"Cycle {t}: Single Error {var_single:.4f} vs Cluster Error {var_cluster:.4f}", flush=True)

    # Final Stats
    mean_single = np.mean(history_single_variance)
    mean_cluster = np.mean(history_cluster_variance)
    
    print("-" * 40)
    print(f"Final Results (N={CYCLES} cycles)")
    print(f"Average Single Phase Error: {mean_single:.4f}")
    print(f"Average Cluster Phase Error: {mean_cluster:.4f}")
    
    improvement = mean_single / mean_cluster if mean_cluster > 0 else 0.0
    print(f"Stability Gain: {improvement:.2f}x")
    
    expected_gain = np.sqrt(10.0) # approx sqrt(N) since we grouped by 10
    print(f"Theoretical Gain (sqrt(N)): ~{expected_gain:.2f}x")
    
    if improvement > 1.5:
        print("SUCCESS: Phase Memory Confirmed. Clusters are stable information carriers.")
    else:
        print("FAILURE: No significant stability gain.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
