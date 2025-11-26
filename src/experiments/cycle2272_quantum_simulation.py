
import sys
import os
import numpy as np
import random
from typing import List, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent

class QuantumAgent(FractalAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Quantum State: Probability Amplitude (Real, Imaginary)
        # Represented as a 2D vector for simplicity in interaction
        self.psi = np.array([1.0, 0.0]) # |0> state initialized
        
    def normalize(self):
        norm = np.linalg.norm(self.psi)
        if norm > 0:
            self.psi /= norm
            
    def superposition(self):
        # Hadamard Gate-like operation
        # |0> -> (|0> + |1>) / sqrt(2)
        # Transform: [[1, 1], [1, -1]] / sqrt(2)
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self.psi = np.dot(H, self.psi)
        self.normalize()
        
    def measure(self) -> int:
        # Collapse wavefunction
        prob_0 = self.psi[0]**2
        if random.random() < prob_0:
            self.psi = np.array([1.0, 0.0])
            return 0
        else:
            self.psi = np.array([0.0, 1.0])
            return 1

def run_quantum_experiment():
    print("MOG ONLINE: Cycle 2272 - Quantum Simulation", flush=True)
    
    N_AGENTS = 1000
    agents = [QuantumAgent(agent_id=f"q_{i}") for i in range(N_AGENTS)]
    
    print("Phase 1: Initialization (|0>)")
    measurements = [a.measure() for a in agents]
    zeros = measurements.count(0)
    print(f"Measured 0s: {zeros}/{N_AGENTS} (Expected ~1000)")
    
    # Reset
    agents = [QuantumAgent(agent_id=f"q_{i}") for i in range(N_AGENTS)]
    
    print("\nPhase 2: Superposition (Hadamard)")
    for a in agents:
        a.superposition()
        
    measurements = [a.measure() for a in agents]
    zeros = measurements.count(0)
    ones = measurements.count(1)
    
    print(f"Measured 0s: {zeros}")
    print(f"Measured 1s: {ones}")
    ratio = zeros / N_AGENTS
    print(f"Ratio 0: {ratio:.4f} (Expected 0.5000)")
    
    if 0.45 < ratio < 0.55:
        print("SUCCESS: Superposition demonstrated.")
        return True
    else:
        print("FAILURE: Statistics deviate from Quantum Prediction.")
        return False

if __name__ == "__main__":
    run_quantum_experiment()
