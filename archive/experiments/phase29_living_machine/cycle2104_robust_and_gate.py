
import sys
import os
import random
import numpy as np
from typing import List, Dict, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

def apply_phase_noise(agent: FractalAgent, noise_strength: float):
    noise = np.random.normal(0, noise_strength)
    agent.state.phase = (agent.state.phase + noise) % (2 * np.pi)

def get_cluster_phase(constituents: List[FractalAgent]) -> float:
    sin_sum = sum(np.sin(c.state.phase) for c in constituents)
    cos_sum = sum(np.cos(c.state.phase) for c in constituents)
    return np.arctan2(sin_sum, cos_sum)

def create_cluster(N_AGENTS: int, WORLD_SIZE: float, comp_engine: CompositionEngine, initial_phase: float, offset_pos: np.ndarray) -> Tuple[FractalAgent, List[FractalAgent]]:
    agents = []
    for i in range(N_AGENTS):
        pos = offset_pos + np.random.rand(3) * 5.0
        agent = FractalAgent(
            agent_id=f"node_{random.randint(0,999999)}",
            energy=1.0,
            phase=initial_phase, 
            position=pos
        )
        agents.append(agent)

    clusters = comp_engine.compose_all(agents)
    if not clusters:
        return None, agents 

    parent = clusters[0]
    constituents = [a for a in agents if a.state.parent_id == parent.state.agent_id]
    return parent, constituents

def run_logic_test(input_a_val: float, input_b_val: float, control_type: str) -> float:
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    NOISE_STRENGTH = 0.5
    COUPLING_K = 0.1
    DRIVE_K = 0.2
    CYCLES = 200
    
    comp_engine = CompositionEngine(resonance_threshold=0.1, energy_threshold=0.1)
    
    # 1. Create Inputs (Simulated by driving clusters to fixed states)
    # We don't simulate Input clusters, we just use the values to drive the Output cluster.
    # The "Output Cluster" represents the gate body.
    
    # Logic:
    # Target = Pi if (A ~ Pi and B ~ Pi) else 0
    # But how does the physics do it?
    # Interference: Target Phase = (Phase A + Phase B).
    # If 0+0=0. If Pi+0=Pi. If 0+Pi=Pi. If Pi+Pi=2Pi=0.
    # This is XOR (or Parity). 
    # To get AND, we need non-linearity.
    # Threshold Logic: If (Input > Threshold) -> 1.
    
    # Let's simulate the Output Cluster receiving signals from A and B.
    # Signal = sin(PhaseA - PhaseOutput) + sin(PhaseB - PhaseOutput).
    # If we drive the Output Cluster with this sum, it will align with the vector sum.
    
    # BUT we want AND.
    # Let's use the "Bang-Bang" idea on the *sum* of inputs.
    # Driving Force = sign( sin(A-O) + sin(B-O) - BIAS )?
    # No, simple physical superposition:
    # Drive = k * (sin(A - O) + sin(B - O))
    # If A=Pi, B=Pi: sin(Pi-O) + sin(Pi-O) = -2sin(O). Stable at O=Pi?
    # Let's check: If O=Pi, sin(0) + sin(0) = 0. Stable.
    # If A=0, B=0: sin(0-O) + sin(0-O) = -2sin(O). Stable at O=0.
    # If A=Pi, B=0: sin(Pi-O) + sin(0-O) = sin(Pi)*cos(O) - cos(Pi)*sin(O) - sin(O) = 0 - (-1)sin(O) - sin(O) = 0.
    # Wait. sin(Pi-x) = sin(x).
    # So sin(Pi-O) + sin(-O) = sin(O) - sin(O) = 0.
    # At A=Pi, B=0, the forces CANCEL. The output floats.
    # This is not AND.
    
    # To make AND, we need a BIAS term.
    # Drive = k * (sin(A-O) + sin(B-O) + sin(Bias-O))
    # Let Bias = 0. Strength = 1.0?
    # If A=Pi, B=Pi: Force = 0 + 0 + sin(0-O) -> Pulls to 0?
    # We want Pi.
    
    # Let's re-evaluate Cycle 1983 NOT Gate. How did that work?
    # Likely just drove Target = Pi - Input.
    
    # Biological AND gate (Gene Regulatory Network):
    # Promoter A + Promoter B needed to recruit Polymerase.
    
    # Physical AND gate (Acoustic):
    # Constructive interference at target point ONLY if A and B are in phase?
    # If we define "1" as "High Energy at Output Node".
    # A sends wave to O. B sends wave to O.
    # If in phase (both 0 or both Pi), they sum to 2.
    # If anti-phase (0 and Pi), they sum to 0.
    # This is XNOR (Equality). 0,0->1. Pi,Pi->1. 0,Pi->0.
    
    # Okay, we want AND: 0,0->0. 0,1->0. 1,0->0. 1,1->1.
    # Let 0 = Phase 0. 1 = Phase Pi.
    # We want Output Phase to be Pi ONLY if A=Pi and B=Pi.
    # Otherwise Output Phase should be 0.
    
    # We can simply define the "Target Phase" calculation using a non-linear function,
    # then use the Bang-Bang controller to drive the cluster to that target.
    # This assumes the "computation" happens in the signal integration step (e.g. at the membrane).
    
    # Computation:
    # Combined_Signal = (Vector_A + Vector_B).
    # If |Combined_Signal| > Threshold?
    # No, let's stick to phase.
    
    # Strategy: Biased Competition.
    # Input A pulls towards Pi. Input B pulls towards Pi.
    # A strong bias pulls towards 0.
    # Force = k_input * sin(Pi - O) + k_input * sin(Pi - O) + k_bias * sin(0 - O).
    # If k_bias > k_input but k_bias < 2*k_input:
    # Case 0,0: Pulls to 0.
    # Case 1,0: 1 pull to Pi, 1 pull to 0 (Bias). Bias wins (if k_bias > k_input). Result 0.
    # Case 1,1: 2 pulls to Pi, 1 pull to 0. Input wins (2*k > k_bias). Result Pi.
    # THIS IS A THRESHOLD LOGIC GATE using Forces!
    
    # Parameters for Logic:
    k_input = 1.0
    k_bias = 1.5 # 1.0 < 1.5 < 2.0
    
    # Setup Output Cluster
    # Initial phase random
    output_parent, output_constituents = create_cluster(N_AGENTS, WORLD_SIZE, comp_engine, random.uniform(0, 2*np.pi), np.array([50.0, 50.0, 0.0]))
    
    if not output_parent: return 0.0
    
    for t in range(CYCLES):
        mean_phase = get_cluster_phase(output_constituents)
        
        for child in output_constituents:
            # 1. Internal Cohesion
            f_int = COUPLING_K * np.sin(mean_phase - child.state.phase)
            
            # 2. Logic Drive (The Computation)
            # Input A pull (towards input_a_val)
            f_a = k_input * np.sin(input_a_val - child.state.phase)
            # Input B pull (towards input_b_val)
            f_b = k_input * np.sin(input_b_val - child.state.phase)
            # Bias pull (towards 0)
            f_bias = k_bias * np.sin(0.0 - child.state.phase)
            
            total_drive = f_a + f_b + f_bias
            
            # 3. Apply Control Strategy (The Robustness Layer)
            if control_type == "Linear":
                f_ext = DRIVE_K * total_drive
            elif control_type == "Bang-Bang":
                f_ext = DRIVE_K * np.sign(total_drive)
            
            child.state.phase += f_int + f_ext
            apply_phase_noise(child, NOISE_STRENGTH)
            
    final_phase = get_cluster_phase(output_constituents)
    # Convert to 0 or 1 (Threshold at Pi/2)
    # Dist to 0:
    dist_0 = min(abs(final_phase - 0), 2*np.pi - abs(final_phase - 0))
    dist_pi = min(abs(final_phase - np.pi), 2*np.pi - abs(final_phase - np.pi))
    
    return 1.0 if dist_pi < dist_0 else 0.0

def run_experiment():
    print("MOG ONLINE: Cycle 2104 - The Robust AND Gate", flush=True)
    print("Integrating Cycle 1985 findings (Bang-Bang) to solve Cycle 1984 (Logic Gate).", flush=True)
    
    truth_table = [
        (0.0, 0.0, 0.0),
        (0.0, np.pi, 0.0),
        (np.pi, 0.0, 0.0),
        (np.pi, np.pi, 1.0)
    ]
    
    for control in ["Linear", "Bang-Bang"]:
        print(f"\n--- Testing Control: {control} ---", flush=True)
        score = 0
        for a, b, expected in truth_table:
            result = run_logic_test(a, b, control)
            status = "PASS" if result == expected else "FAIL"
            if result == expected: score += 1
            
            a_sym = "1" if a > 0 else "0"
            b_sym = "1" if b > 0 else "0"
            print(f"Input {a_sym},{b_sym} -> Output {result} (Expected {expected}) : {status}", flush=True)
            
        print(f"Total Score: {score}/4")
        
    print("\nCONCLUSION: Bang-Bang control should stabilize the logic threshold in noise.")

if __name__ == "__main__":
    run_experiment()
