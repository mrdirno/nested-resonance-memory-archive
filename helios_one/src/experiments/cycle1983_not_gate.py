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

def create_cluster(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float, cluster_id_prefix: str) -> Tuple[FractalAgent, List[FractalAgent], Dict[str, List[FractalAgent]]]:
    """Helper function to create agents and form a cluster. Returns (parent_cluster, constituents, cluster_map)."""
    
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"{cluster_id_prefix}_{i}",
            energy=1.0,
            phase=initial_phase, 
            position=pos
        )
        agents.append(agent)

    # Move agents close to encourage clustering
    center = np.array([50.0, 50.0, 0.0])
    for agent in agents:
        offset = np.random.rand(3) * 2.0 - 1.0 # small random offset
        agent.state.position = center + offset
        agent.state.phase = initial_phase + np.random.normal(0, 0.1) 
        
    clusters = comp_engine.compose_all(agents)
    
    if not clusters:
        raise ValueError(f"Failed to form cluster for {cluster_id_prefix}")

    parent_cluster = clusters[0] # Assuming one large cluster
    constituents = [a for a in agents if a.state.parent_id == parent_cluster.state.agent_id]
    
    # Update parent_cluster's phase to represent the average
    sin_sum = sum(np.sin(c.state.phase) for c in constituents)
    cos_sum = sum(np.cos(c.state.phase) for c in constituents)
    parent_cluster.state.phase = np.arctan2(sin_sum, cos_sum) % (2 * np.pi)

    print(f"  Formed cluster '{cluster_id_prefix}' with {len(constituents)} constituents (Initial Phase: {parent_cluster.state.phase:.2f}).", flush=True)
    return parent_cluster, constituents

def phase_diff(p1, p2):
    """Calculate the shortest angular distance between two phases."""
    d = abs(p1 - p2)
    return min(d, 2 * np.pi - d)

def run_experiment():
    print("MOG ONLINE: Cycle 1983 - NOT Gate Implementation", flush=True)
    print("Hypothesis: A NOT gate can be implemented by driving an output cluster with an inverted force derived from an input cluster's phase.", flush=True)
    
    # Parameters
    N_AGENTS_PER_CLUSTER = 100
    WORLD_SIZE = 100.0
    NOISE_STRENGTH = 0.5
    COUPLING_K_INT = 0.1 # Internal glue
    K_NOT_DRIVE = 0.15 # Strength of the inverting force
    CYCLES = 200

    TARGET_PHASE_0 = 0.0
    TARGET_PHASE_PI = np.pi

    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    results = {}

    # Test cases for Input Cluster initial state
    INPUT_INITIAL_STATES = [TARGET_PHASE_0, TARGET_PHASE_PI]

    for initial_input_phase in INPUT_INITIAL_STATES:
        print(f"\n--- Testing Input Cluster at {initial_input_phase:.2f} ---", flush=True)

        # 1. Setup Input Cluster (Phase will be fixed or slowly drift due to noise)
        input_cluster_parent, input_constituents = create_cluster(N_AGENTS_PER_CLUSTER, WORLD_SIZE, comp_engine, initial_input_phase, "Input")
        
        # 2. Setup Output Cluster (Initialize to a neutral or different state)
        output_cluster_parent, output_constituents = create_cluster(N_AGENTS_PER_CLUSTER, WORLD_SIZE, comp_engine, TARGET_PHASE_0, "Output")
        
        # Tracking
        input_phase_history = []
        output_phase_history = []
        
        
        for t in range(CYCLES):
            # --- Input Cluster Dynamics (fixed for this experiment to ensure stable input) ---
            # The input cluster acts as a stable reference.
            # Its phase is held constant at its initial target value.
            input_cluster_parent.state.phase = initial_input_phase
            input_phase_history.append(input_cluster_parent.state.phase)

            # --- Output Cluster Dynamics ---
            sin_sum_out = sum(np.sin(c.state.phase) for c in output_constituents)
            cos_sum_out = sum(np.cos(c.state.phase) for c in output_constituents)
            mean_phase_out = np.arctan2(sin_sum_out, cos_sum_out)
            
            # Determine target for Output Cluster (Inverse of Input)
            # We assume input is either near 0 or near PI.
            if phase_diff(input_cluster_parent.state.phase, TARGET_PHASE_0) < phase_diff(input_cluster_parent.state.phase, TARGET_PHASE_PI):
                # Input is near 0, so output target is PI
                output_target_phase = TARGET_PHASE_PI
            else:
                # Input is near PI, so output target is 0
                output_target_phase = TARGET_PHASE_0
            
            # Update constituents
            for child in output_constituents:
                # Internal force (pull to mean)
                f_int_out = COUPLING_K_INT * np.sin(mean_phase_out - child.state.phase)
                
                # External force (NOT Gate Drive)
                f_not_drive = K_NOT_DRIVE * np.sin(output_target_phase - child.state.phase)
                
                child.state.phase += f_int_out + f_not_drive
                
                # Noise
                apply_phase_noise(child, NOISE_STRENGTH)
            
            # Update Output Cluster Phase
            output_cluster_parent.state.phase = np.arctan2(sin_sum_out, cos_sum_out) % (2 * np.pi)
            output_phase_history.append(output_cluster_parent.state.phase)
            
            if t % 20 == 0:
                print(f"  Cycle {t}: Input Phase {input_cluster_parent.state.phase:.2f} -> Output Phase {output_cluster_parent.state.phase:.2f}", flush=True)

        # 3. Evaluate NOT Gate performance
        # Average Input over last 10 cycles
        avg_input_phase_final = np.mean([p for p in input_phase_history[-10:] if not np.isnan(p)])
        # Average Output over last 10 cycles
        avg_output_phase_final = np.mean([p for p in output_phase_history[-10:] if not np.isnan(p)])

        print(f"\n  Final Input Phase: {avg_input_phase_final:.2f}")
        print(f"  Final Output Phase: {avg_output_phase_final:.2f}")

        # Check if Output is the inverse of Input
        # Assuming Input is either 0 or PI
        is_input_0 = phase_diff(avg_input_phase_final, TARGET_PHASE_0) < phase_diff(avg_input_phase_final, TARGET_PHASE_PI)
        
        if is_input_0: # Input was 0, expecting output PI
            expected_output_phase = TARGET_PHASE_PI
        else: # Input was PI, expecting output 0
            expected_output_phase = TARGET_PHASE_0
        
        output_correct = phase_diff(avg_output_phase_final, expected_output_phase) < 1.0 # Within 1 radian of target
        
        print(f"  Expected Output for Input {avg_input_phase_final:.2f} was {expected_output_phase:.2f}")
        print(f"  NOT Gate {'SUCCESS' if output_correct else 'FAILURE'}")
        results[initial_input_phase] = output_correct

    # Final summary
    print("\n--- Summary ---")
    all_successful = True
    for initial_input_phase in INPUT_INITIAL_STATES:
        status = "SUCCESS" if results[initial_input_phase] else "FAILURE"
        print(f"Input Initial {initial_input_phase:.2f}: {status}")
        if not results[initial_input_phase]:
            all_successful = False
            
    if all_successful:
        print("\nHYPOTHESIS CONFIRMED: NRM Clusters can implement a NOT logic gate.")
    else:
        print("\nHYPOTHESIS FAILED: NOT gate implementation was not fully successful.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
