
"""
Cycle 2287: Quantum Superposition
Goal: Implement probabilistic state (Superposition) in Fractal Agents.
Phase 40: Quantum Dynamics

Hypothesis: Agents can exist in multiple potential states simultaneously until 'measured'.
"""

import sys
import os
import numpy as np
import time
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from core.fractal_agent import FractalAgent

class QuantumFractalAgent(FractalAgent):
    """
    Fractal Agent with Quantum Capabilities (Superposition).
    State is represented by a wavefunction (complex vector).
    """
    def __init__(self, agent_id: str, n_states: int = 2):
        super().__init__(agent_id)
        self.n_states = n_states
        # Initialize in state |0>
        self.wavefunction = np.zeros(n_states, dtype=np.complex128)
        self.wavefunction[0] = 1.0 + 0j
        
    def apply_hadamard(self):
        """
        Apply Hadamard gate to put agent in superposition.
        H |0> -> (|0> + |1>) / sqrt(2)
        """
        # Simple 2-state H-gate matrix
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self.wavefunction = np.dot(H, self.wavefunction)
        
    def measure(self) -> int:
        """
        Collapse wavefunction and return observed state index.
        P(i) = |coeff_i|^2
        """
        probs = np.abs(self.wavefunction) ** 2
        # Normalize to ensure sum is exactly 1.0 (floating point fix)
        probs /= np.sum(probs)
        
        # Collapse
        state = np.random.choice(self.n_states, p=probs)
        
        # Update wavefunction to reflect collapsed state
        self.wavefunction = np.zeros(self.n_states, dtype=np.complex128)
        self.wavefunction[state] = 1.0 + 0j
        
        return state

def run_experiment():
    print("Initializing Cycle 2287: Quantum Superposition...")
    
    # 1. Create Quantum Agent
    q_agent = QuantumFractalAgent("Q-001")
    print(f"Agent Initial State (Wavefunction): {q_agent.wavefunction}")
    
    # 2. Apply Superposition
    print("Applying Hadamard Gate (Superposition)...")
    q_agent.apply_hadamard()
    print(f"Agent State after H: {q_agent.wavefunction}")
    
    # 3. Measurement Statistics
    print("Running Measurement Statistics (1000 trials, resetting each time)...")
    counts = {0: 0, 1: 0}
    n_trials = 1000
    
    for _ in range(n_trials):
        # Reset to superposition
        q_agent.wavefunction = np.zeros(2, dtype=np.complex128)
        q_agent.wavefunction[0] = 1.0
        q_agent.apply_hadamard()
        
        # Measure
        result = q_agent.measure()
        counts[result] += 1
        
    print(f"Measurement Results: {counts}")
    
    # 4. Verification
    prob_0 = counts[0] / n_trials
    prob_1 = counts[1] / n_trials
    
    # Expected: ~0.5 each
    error = abs(prob_0 - 0.5)
    print(f"Probability |0>: {prob_0:.3f} (Target 0.5)")
    print(f"Probability |1>: {prob_1:.3f} (Target 0.5)")
    print(f"Error: {error:.3f}")
    
    success = error < 0.05 # Allow 5% variance
    status = "SUCCESS" if success else "FAILURE"
    print(f"Status: {status}")
    
    # Save results
    output_path = "experiments/results/cycle2287_quantum_superposition.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2287,
            "trials": n_trials,
            "counts": counts,
            "probabilities": {"0": prob_0, "1": prob_1},
            "error": error,
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
