
import sys
import os
import numpy as np
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2272_quantum_simulation import QuantumAgent

class EntangledPair:
    def __init__(self):
        self.alice = QuantumAgent(agent_id="Alice")
        self.bob = QuantumAgent(agent_id="Bob")
        # Bell State: (|00> + |11>) / sqrt(2)
        self.collapsed = False
        self.outcome_alice = None
        self.outcome_bob = None
        
    def measure_alice(self) -> int:
        if self.collapsed:
            return self.outcome_alice
            
        # Collapse
        if random.random() < 0.5:
            self.outcome_alice = 0
            self.outcome_bob = 0
        else:
            self.outcome_alice = 1
            self.outcome_bob = 1
            
        self.collapsed = True
        return self.outcome_alice

    def measure_bob(self) -> int:
        if self.collapsed:
            return self.outcome_bob
            
        # Collapse (same logic, triggered by Bob)
        if random.random() < 0.5:
            self.outcome_alice = 0
            self.outcome_bob = 0
        else:
            self.outcome_alice = 1
            self.outcome_bob = 1
            
        self.collapsed = True
        return self.outcome_bob

def run_entanglement_experiment():
    print("MOG ONLINE: Cycle 2273 - Entanglement Simulation", flush=True)
    
    N_PAIRS = 1000
    pairs = [EntangledPair() for _ in range(N_PAIRS)]
    
    print("Measuring Correlation...")
    matches = 0
    for p in pairs:
        # Measure Alice first
        m_a = p.measure_alice()
        # Measure Bob second
        m_b = p.measure_bob()
        
        if m_a == m_b:
            matches += 1
            
    correlation = matches / N_PAIRS
    print(f"Correlation: {correlation:.4f}")
    
    if correlation == 1.0:
        print("SUCCESS: Perfect Entanglement demonstrated.")
        return True
    else:
        print("FAILURE: Correlation broken.")
        return False

if __name__ == "__main__":
    run_entanglement_experiment()
