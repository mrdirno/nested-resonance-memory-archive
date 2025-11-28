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

def create_cluster(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float, cluster_id_prefix: str) -> Tuple[FractalAgent, List[FractalAgent]]:
    """Helper function to create agents and form a cluster. Returns (parent_cluster, constituents)."""
    
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

def is_near_phase(current_phase, target_phase, threshold):
    return phase_diff(current_phase, target_phase) < threshold

def run_experiment():
    print("MOG ONLINE: Cycle 1984 - AND Gate Implementation", flush=True)
    print("Hypothesis: An AND gate can be implemented by driving an output cluster with a force that only aligns it to PI when both inputs are PI, otherwise it aligns to 0.", flush=True)
    
    # Parameters
    N_AGENTS_PER_CLUSTER = 100
    WORLD_SIZE = 100.0
    NOISE_STRENGTH = 0.01
    COUPLING_K_INT = 5.0 # Internal glue
    K_AND_DRIVE = 0.5 # Strength of the AND gate driving force
    CYCLES = 500

    TARGET_PHASE_0 = 0.0
    TARGET_PHASE_PI = np.pi
    PHASE_THRESHOLD = 0.5 # For sensing if input is 'near 0' or 'near PI'

    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    results = {}

    # Test cases for Input Cluster A and B initial states (all 4 combinations)
    INPUT_STATES = [(TARGET_PHASE_0, TARGET_PHASE_0),
                    (TARGET_PHASE_0, TARGET_PHASE_PI),
                    (TARGET_PHASE_PI, TARGET_PHASE_0),
                    (TARGET_PHASE_PI, TARGET_PHASE_PI)]

    for input_a_init, input_b_init in INPUT_STATES:
        print(f"\n--- Testing Inputs (A={input_a_init:.2f}, B={input_b_init:.2f}) ---", flush=True)

        # 1. Setup Input Clusters A and B (phases fixed for stable input)
        input_a_parent, input_a_constituents = create_cluster(N_AGENTS_PER_CLUSTER, WORLD_SIZE, comp_engine, input_a_init, "InputA")
        input_b_parent, input_b_constituents = create_cluster(N_AGENTS_PER_CLUSTER, WORLD_SIZE, comp_engine, input_b_init, "InputB")
        
        # 2. Setup Output Cluster C (Initialize to 0, which is the default output for AND)
        output_c_parent, output_c_constituents = create_cluster(N_AGENTS_PER_CLUSTER, WORLD_SIZE, comp_engine, TARGET_PHASE_0, "OutputC")
        
        # Tracking
        output_phase_history = []
        
        for t in range(CYCLES):
            # --- Input Cluster Dynamics (fixed for this experiment to ensure stable input) ---
            # Their phases are held constant at their initial target values.
            input_a_parent.state.phase = input_a_init
            input_b_parent.state.phase = input_b_init

            # --- Output Cluster C Dynamics ---
            sin_sum_out = sum(np.sin(c.state.phase) for c in output_c_constituents)
            cos_sum_out = sum(np.cos(c.state.phase) for c in output_c_constituents)
            mean_phase_out = np.arctan2(sin_sum_out, cos_sum_out)
            
            # Sense Input A and B to determine driving force for Output C
            is_a_pi = is_near_phase(input_a_parent.state.phase, TARGET_PHASE_PI, PHASE_THRESHOLD)
            is_b_pi = is_near_phase(input_b_parent.state.phase, TARGET_PHASE_PI, PHASE_THRESHOLD)

            # Define target for Output Cluster C based on AND logic
            if is_a_pi and is_b_pi:
                output_target_phase = TARGET_PHASE_PI
            else:
                output_target_phase = TARGET_PHASE_0
            
            # Update constituents
            for child in output_c_constituents:
                # Internal force (pull to mean)
                f_int_out = COUPLING_K_INT * np.sin(mean_phase_out - child.state.phase)
                
                # External force (AND Gate Drive)
                f_and_drive = K_AND_DRIVE * np.sin(output_target_phase - child.state.phase)
                
                child.state.phase += f_int_out + f_and_drive
                
                # Noise
                apply_phase_noise(child, NOISE_STRENGTH)
            
            # Update Output Cluster C Phase
            output_c_parent.state.phase = np.arctan2(sin_sum_out, cos_sum_out) % (2 * np.pi)
            output_phase_history.append(output_c_parent.state.phase)
            
            if t % 20 == 0:
                print(f"  Cycle {t}: Input A={input_a_parent.state.phase:.2f}, B={input_b_parent.state.phase:.2f} -> Output C={output_c_parent.state.phase:.2f} (Target: {output_target_phase:.2f})", flush=True)

        # 3. Evaluate AND Gate performance
        avg_output_phase_final = np.mean([p for p in output_phase_history[-10:] if not np.isnan(p)])

        print(f"\n  Final Output C Phase: {avg_output_phase_final:.2f}")

        # Determine expected output for AND gate
        expected_output = TARGET_PHASE_0
        if is_near_phase(input_a_init, TARGET_PHASE_PI, PHASE_THRESHOLD) and \
           is_near_phase(input_b_init, TARGET_PHASE_PI, PHASE_THRESHOLD):
            expected_output = TARGET_PHASE_PI
        
        output_correct = is_near_phase(avg_output_phase_final, expected_output, PHASE_THRESHOLD)
        
        print(f"  Expected Output for ({input_a_init:.2f}, {input_b_init:.2f}) was {expected_output:.2f}")
        print(f"  AND Gate {'SUCCESS' if output_correct else 'FAILURE'}")
        results[(input_a_init, input_b_init)] = output_correct

    # Final summary
    print("\n--- Summary ---")
    all_successful = True
    for input_a_init, input_b_init in INPUT_STATES:
        status = "SUCCESS" if results[(input_a_init, input_b_init)] else "FAILURE"
        print(f"Inputs ({input_a_init:.2f}, {input_b_init:.2f}): {status}")
        if not results[(input_a_init, input_b_init)]:
            all_successful = False
            
    if all_successful:
        print("\nHYPOTHESIS CONFIRMED: NRM Clusters can implement an AND logic gate.")
    else:
        print("\nHYPOTHESIS FAILED: AND gate implementation was not fully successful.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
