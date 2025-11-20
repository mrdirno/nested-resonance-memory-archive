import sys
import os
import time
import random
import numpy as np
from typing import List, Tuple

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

def generate_patterns(num_patterns: int, num_agents: int) -> np.ndarray:
    """Generates random binary patterns (-1, 1)."""
    return np.random.choice([-1, 1], size=(num_patterns, num_agents))

def compute_hebbian_weights(patterns: np.ndarray) -> np.ndarray:
    """Computes Hebbian weight matrix J_ij = 1/N * sum(xi_i * xi_j)."""
    P, N = patterns.shape
    J = np.dot(patterns.T, patterns) / N
    np.fill_diagonal(J, 0) # No self-coupling
    return J

def get_overlap(agents: List[FractalAgent], pattern: np.ndarray) -> float:
    """Calculates overlap (magnetization) with a specific pattern.
    m = |1/N * sum(xi_i * exp(i * theta_i))|
    """
    if not agents: return 0.0
    N = len(agents)
    phases = np.array([a.state.phase for a in agents])
    # Map phases to complex vectors
    z = np.exp(1j * phases)
    # Calculate overlap: sum(pattern_i * z_i)
    # If pattern_i is 1 and phase is 0 (z=1), product is 1.
    # If pattern_i is -1 and phase is pi (z=-1), product is 1.
    # So perfect match yields m=1.
    overlap = np.abs(np.sum(pattern * z) / N)
    return overlap

def associative_memory_test():
    print("--- HOLOGRAPHIC ASSOCIATIVE MEMORY EXPERIMENT (PAPER 12) ---")
    print("Hypothesis: Swarm stores patterns via Hebbian Coupling and recalls them from cues.")
    
    # Parameters
    N_AGENTS = 100
    N_PATTERNS = 3
    CYCLES = 200
    DT = 0.1
    COUPLING_STRENGTH = 2.0
    
    # 1. Generate Patterns
    print(f"\n1. Generating {N_PATTERNS} Patterns for {N_AGENTS} Agents...")
    patterns = generate_patterns(N_PATTERNS, N_AGENTS)
    
    # Target Pattern is Pattern 0
    target_pattern = patterns[0]
    
    # 2. Compute Weights (Learning)
    print("2. Computing Hebbian Weights (Imprinting)...")
    J = compute_hebbian_weights(patterns)
    
    # 3. Initialize Swarm with Noisy Cue
    print("3. Initializing Swarm with Partial Cue (Pattern 0 + Noise)...")
    swarm = FractalSwarm(max_agents=N_AGENTS, burst_threshold=200.0)
    
    # Create agents
    agents = []
    for i in range(N_AGENTS):
        agent = swarm.spawn_agent(reality_metrics={}, initial_energy=50.0)
        agents.append(agent)
        
    # Set initial state: Target Pattern + Noise
    # Map -1 -> pi, 1 -> 0
    # Add random perturbation
    noise_level = 0.5 # Radians standard deviation
    
    initial_phases = []
    for i, val in enumerate(target_pattern):
        base_phase = 0.0 if val == 1 else np.pi
        noise = np.random.normal(0, noise_level)
        phase = (base_phase + noise) % (2 * np.pi)
        agents[i].state.phase = phase
        initial_phases.append(phase)
        
    initial_overlap = get_overlap(agents, target_pattern)
    print(f"Initial Overlap with Target: {initial_overlap:.4f}")
    
    # Check overlap with other patterns (should be low)
    for p_idx in range(1, N_PATTERNS):
        ov = get_overlap(agents, patterns[p_idx])
        print(f"Initial Overlap with Pattern {p_idx}: {ov:.4f}")
        
    # 4. Recall Loop (Dynamics)
    print("\n4. Running Recall Dynamics...")
    overlaps = []
    
    for t in range(CYCLES):
        # Calculate field for each agent
        # d(theta_i)/dt = K * sum_j J_ij * sin(theta_j - theta_i)
        
        current_phases = np.array([a.state.phase for a in agents])
        
        # Vectorized update
        # We need sum_j J_ij * sin(theta_j - theta_i)
        # This is O(N^2). For N=100, it's fine.
        
        # Create matrix of phase differences: D_ij = theta_j - theta_i
        # theta_j is row vector, theta_i is col vector
        phase_diffs = current_phases[None, :] - current_phases[:, None]
        interactions = np.sin(phase_diffs)
        
        # Weighted sum
        forces = np.sum(J * interactions, axis=1)
        
        # Update phases
        for i, agent in enumerate(agents):
            # Apply coupling force
            d_theta = COUPLING_STRENGTH * forces[i] * DT
            agent.state.phase = (agent.state.phase + d_theta) % (2 * np.pi)
            
            # Apply natural evolution (optional, assume identical freq 0 for memory)
            # If we add natural freq, it becomes a rotating frame
            # For pure memory, we assume static frame (omega=0)
            
        # Measure Overlap
        ov = get_overlap(agents, target_pattern)
        overlaps.append(ov)
        
        if t % 20 == 0:
            print(f"Cycle {t}: Overlap = {ov:.4f}")
            
    # 5. Analysis
    print("\n--- ANALYSIS ---")
    final_overlap = overlaps[-1]
    print(f"Final Overlap with Target: {final_overlap:.4f}")
    
    # Check others
    print("Final Overlaps with other patterns:")
    for p_idx in range(1, N_PATTERNS):
        ov = get_overlap(agents, patterns[p_idx])
        print(f"Pattern {p_idx}: {ov:.4f}")
        
    if final_overlap > 0.9:
        print("SUCCESS: Swarm recalled target pattern.")
    else:
        print("FAILURE: Did not converge to target.")

if __name__ == "__main__":
    associative_memory_test()
