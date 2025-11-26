
"""
Cycle 2288: Quantum Entanglement
Goal: Implement shared state (Non-Locality) between two Fractal Agents.
Phase 40: Quantum Dynamics

Hypothesis: Measurement of one entangled agent instantaneously determines the state of the other.
"""

import sys
import os
import numpy as np
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from experiments.cycle2287_quantum_superposition import QuantumFractalAgent

class EntangledSystem:
    """
    Manages joint quantum state for two agents.
    State vector size: 2^2 = 4 basis states (|00>, |01>, |10>, |11>)
    """
    def __init__(self, agent_a: QuantumFractalAgent, agent_b: QuantumFractalAgent):
        self.agent_a = agent_a
        self.agent_b = agent_b
        # Initialize |00>
        self.joint_wavefunction = np.zeros(4, dtype=np.complex128)
        self.joint_wavefunction[0] = 1.0 + 0j
        
    def apply_bell_circuit(self):
        """
        Create Bell State (|00> + |11>) / sqrt(2)
        1. H on Agent A
        2. CNOT (A control, B target)
        """
        # 1. H on A (Tensor product H x I)
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        I = np.eye(2)
        H_I = np.kron(H, I)
        
        self.joint_wavefunction = np.dot(H_I, self.joint_wavefunction)
        
        # 2. CNOT (A control, B target)
        # Maps |10> -> |11> and |11> -> |10> (if we order A, B)
        # Basis: 00, 01, 10, 11
        # CNOT Matrix:
        # 1 0 0 0
        # 0 1 0 0
        # 0 0 0 1
        # 0 0 1 0
        CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        
        self.joint_wavefunction = np.dot(CNOT, self.joint_wavefunction)
        
    def measure_a(self) -> int:
        """
        Measure Agent A. Collapses joint state.
        Returns 0 or 1.
        """
        # Prob(A=0) = P(00) + P(01)
        # Prob(A=1) = P(10) + P(11)
        probs = np.abs(self.joint_wavefunction) ** 2
        prob_a0 = probs[0] + probs[1]
        prob_a1 = probs[2] + probs[3]
        
        # Normalize sum (float errors)
        total = prob_a0 + prob_a1
        prob_a0 /= total
        prob_a1 /= total
        
        # Measurement
        result = np.random.choice([0, 1], p=[prob_a0, prob_a1])
        
        # Collapse
        # If A=0, keep 00 and 01, zero out 10 and 11
        # If A=1, zero out 00 and 01, keep 10 and 11
        if result == 0:
            self.joint_wavefunction[2] = 0
            self.joint_wavefunction[3] = 0
        else:
            self.joint_wavefunction[0] = 0
            self.joint_wavefunction[1] = 0
            
        # Renormalize
        norm = np.linalg.norm(self.joint_wavefunction)
        if norm > 0:
            self.joint_wavefunction /= norm
            
        return result

    def measure_b(self) -> int:
        """
        Measure Agent B. Collapses joint state.
        Returns 0 or 1.
        """
        # Prob(B=0) = P(00) + P(10)
        # Prob(B=1) = P(01) + P(11)
        probs = np.abs(self.joint_wavefunction) ** 2
        prob_b0 = probs[0] + probs[2]
        prob_b1 = probs[1] + probs[3]
        
        total = prob_b0 + prob_b1
        if total == 0: return 0 # Should not happen if normalized
        prob_b0 /= total
        prob_b1 /= total
        
        result = np.random.choice([0, 1], p=[prob_b0, prob_b1])
        
        # Collapse
        if result == 0:
            self.joint_wavefunction[1] = 0
            self.joint_wavefunction[3] = 0
        else:
            self.joint_wavefunction[0] = 0
            self.joint_wavefunction[2] = 0
            
        norm = np.linalg.norm(self.joint_wavefunction)
        if norm > 0:
            self.joint_wavefunction /= norm
            
        return result

def run_experiment():
    print("Initializing Cycle 2288: Quantum Entanglement...")
    
    agent_a = QuantumFractalAgent("Alice")
    agent_b = QuantumFractalAgent("Bob")
    system = EntangledSystem(agent_a, agent_b)
    
    print("Applying Bell Circuit (Entanglement)...")
    system.apply_bell_circuit()
    print(f"Joint State: {system.joint_wavefunction}")
    # Expected: [0.707 0 0 0.707] approx
    
    print("Running Correlation Test (1000 trials)...")
    matches = 0
    n_trials = 1000
    
    for _ in range(n_trials):
        # Reset
        system.joint_wavefunction = np.zeros(4, dtype=np.complex128)
        system.joint_wavefunction[0] = 1.0
        system.apply_bell_circuit()
        
        # Measure A then B
        res_a = system.measure_a()
        res_b = system.measure_b()
        
        if res_a == res_b:
            matches += 1
            
    correlation = matches / n_trials
    print(f"Correlation: {correlation:.4f}")
    
    success = correlation > 0.99 # Expect 1.0
    status = "SUCCESS" if success else "FAILURE"
    print(f"Status: {status}")
    
    # Save results
    output_path = "experiments/results/cycle2288_quantum_entanglement.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2288,
            "trials": n_trials,
            "matches": matches,
            "correlation": correlation,
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
