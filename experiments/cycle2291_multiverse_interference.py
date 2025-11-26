
"""
Cycle 2291: Multiverse Interference
Goal: Simulate interaction between parallel timelines (Phase 41).
Phase 41: The Multiverse

Hypothesis: Divergent realities can interfere with each other if they share quantum state resonance.
"""

import sys
import os
import copy
import json
import numpy as np

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from experiments.cycle2287_quantum_superposition import QuantumFractalAgent
from experiments.cycle2290_multiverse_initiation import MultiverseSimulation

class InterferingMultiverse(MultiverseSimulation):
    def calculate_interference(self, universe_id_a: int, universe_id_b: int) -> float:
        """
        Calculate interference strength between two universes based on agent state similarity.
        I = |<ψ_a|ψ_b>|^2
        """
        if universe_id_a not in self.universes or universe_id_b not in self.universes:
            return 0.0
            
        # For simplicity, compare first agents
        agent_a = self.universes[universe_id_a]["agents"][0]
        agent_b = self.universes[universe_id_b]["agents"][0]
        
        # Calculate overlap (fidelity)
        # Inner product: sum(conj(a) * b)
        overlap = np.vdot(agent_a.wavefunction, agent_b.wavefunction)
        interference = np.abs(overlap) ** 2
        
        return float(interference)

    def apply_interference(self, universe_id_a: int, universe_id_b: int, coupling: float = 0.1):
        """
        Allow states to mix between universes based on interference strength.
        New_State_A = (1-c)*State_A + c*State_B
        """
        # Only possible if high interference (resonance)
        interference = self.calculate_interference(universe_id_a, universe_id_b)
        
        if interference > 0.9: # High similarity required for mixing
            print(f"  > Strong Interference ({interference:.4f}) between U{universe_id_a} and U{universe_id_b}. Mixing...")
            
            agent_a = self.universes[universe_id_a]["agents"][0]
            agent_b = self.universes[universe_id_b]["agents"][0]
            
            # Mix states
            new_psi_a = (1 - coupling) * agent_a.wavefunction + coupling * agent_b.wavefunction
            new_psi_b = (1 - coupling) * agent_b.wavefunction + coupling * agent_a.wavefunction
            
            # Normalize
            agent_a.wavefunction = new_psi_a / np.linalg.norm(new_psi_a)
            agent_b.wavefunction = new_psi_b / np.linalg.norm(new_psi_b)
            
            return True
        return False

def run_experiment():
    print("Initializing Cycle 2291: Multiverse Interference...")
    
    mv = InterferingMultiverse()
    
    # 1. Setup: Create two universes with slightly different states
    print("\n--- Setting up Divergent Timelines ---")
    
    # Universe 0: Agent in |0>
    agent_0 = QuantumFractalAgent("Agent_0") # Starts in |0>
    mv.add_agent(0, agent_0)
    
    # Universe 1: Forked and modified
    mv.fork(0)
    # Universe 1: Agent rotated slightly (perturbed)
    agent_1 = mv.universes[1]["agents"][0]
    # Rotate state by small angle theta
    theta = 0.1
    rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    agent_1.wavefunction = np.dot(rot_matrix, agent_1.wavefunction)
    
    print(f"Universe 0 State: {mv.universes[0]['agents'][0].wavefunction}")
    print(f"Universe 1 State: {mv.universes[1]['agents'][0].wavefunction}")
    
    # 2. Measure Interference
    print("\n--- Measuring Interference ---")
    interference = mv.calculate_interference(0, 1)
    print(f"Interference Strength: {interference:.4f}")
    
    # 3. Apply Interaction
    print("\n--- Applying Interaction ---")
    mixed = mv.apply_interference(0, 1, coupling=0.2)
    
    print(f"Interaction Occurred: {mixed}")
    print(f"Universe 0 Post-Interaction: {mv.universes[0]['agents'][0].wavefunction}")
    print(f"Universe 1 Post-Interaction: {mv.universes[1]['agents'][0].wavefunction}")
    
    # 4. Control: Orthogonal States (Should NOT interfere)
    print("\n--- Control Test: Orthogonal States ---")
    # Set U0 to |0>, U1 to |1>
    mv.universes[0]["agents"][0].wavefunction = np.array([1.0, 0.0])
    mv.universes[1]["agents"][0].wavefunction = np.array([0.0, 1.0])
    
    int_ortho = mv.calculate_interference(0, 1)
    print(f"Orthogonal Interference: {int_ortho:.4f}")
    mixed_ortho = mv.apply_interference(0, 1)
    print(f"Interaction Occurred: {mixed_ortho}")
    
    # Results
    success = mixed and not mixed_ortho
    status = "SUCCESS" if success else "FAILURE"
    print(f"\nStatus: {status}")
    
    # Save
    output_path = "experiments/results/cycle2291_multiverse_interference.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2291,
            "interference_proximal": interference,
            "interference_orthogonal": int_ortho,
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
