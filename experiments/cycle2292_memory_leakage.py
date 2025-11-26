
"""
Cycle 2292: Cross-Timeline Memory Leakage
Goal: Test if memories can "leak" between divergent timelines via resonance.
Phase 41: The Multiverse

Hypothesis: If two universes are resonant (highly similar), memories stored in one can be retrieved in the other.
"""

import sys
import os
import numpy as np
import json
import copy

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from experiments.cycle2287_quantum_superposition import QuantumFractalAgent
from experiments.cycle2290_multiverse_initiation import MultiverseSimulation
from experiments.cycle2291_multiverse_interference import InterferingMultiverse
from memory.pattern_memory import PatternMemory

class MultiverseMemory(InterferingMultiverse):
    """
    Extends MultiverseSimulation to include PatternMemory in each universe.
    """
    def __init__(self):
        super().__init__()
        # Each universe gets its own isolated memory system
        self.memories = {0: PatternMemory(dimension=1024, partitions=8)}
        
    def fork(self, universe_id: int) -> int:
        """
        Override fork to deep copy memory as well.
        """
        new_id = super().fork(universe_id)
        if new_id != -1:
            # Deep copy the memory system
            self.memories[new_id] = copy.deepcopy(self.memories[universe_id])
        return new_id
        
    def leak_memory(self, source_uid: int, target_uid: int, key: str) -> str:
        """
        Attempt to retrieve a memory from a target universe that was only stored in the source universe.
        Success depends on interference strength (resonance).
        """
        interference = self.calculate_interference(source_uid, target_uid)
        print(f"  > Resonance between U{source_uid} and U{target_uid}: {interference:.4f}")
        
        if interference > 0.9:
            print(f"  > Resonance Critical! Quantum Tunneling of Information enabled.")
            # Tunneling: Access source memory directly (simulating leakage)
            # In a real quantum system, this would be via entanglement or shared wavefunction
            # Here we simulate it by allowing access if resonance is high
            val = self.memories[source_uid].retrieve(key)
            return val
        else:
            print(f"  > Resonance too low. Timeline isolation maintained.")
            return None

def run_experiment():
    print("Initializing Cycle 2292: Cross-Timeline Memory Leakage...")
    
    mv = MultiverseMemory()
    
    # 1. Setup Timeline A (Universe 0)
    agent_0 = QuantumFractalAgent("Traveler")
    mv.add_agent(0, agent_0)
    
    print("\n--- Timeline 0: The Origin ---")
    secret_key = "Winning_Lottery_Numbers"
    secret_val = "4 8 15 16 23 42"
    mv.memories[0].store(secret_key, secret_val)
    print(f"Stored secret in U0: {secret_val}")
    
    # 3. Fork to Timeline B (Universe 1) - High Resonance
    print("\n--- Forking Timeline 1 (High Resonance) ---")
    mv.fork(0)
    # Slight divergence (small rotation)
    theta = 0.05
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    
    # Access object attribute directly, not as dict
    agent_1 = mv.universes[1]["agents"][0]
    agent_1.wavefunction = np.dot(rot, agent_1.wavefunction)
    
    # 4. Fork to Timeline C (Universe 2) - Low Resonance (Orthogonal)
    print("\n--- Forking Timeline 2 (Low Resonance) ---")
    mv.fork(0)
    # Major divergence (Orthogonal flip)
    agent_2 = mv.universes[2]["agents"][0]
    agent_2.wavefunction = np.array([0.0, 1.0]) # Assuming starts at |0>
    
    # 4. Test Leakage
    print("\n--- Testing Leakage from U0 to U1 (Resonant) ---")
    # Note: In U1 memory, the key exists because it was forked *after* storage.
    # To test leakage, we need to store something NEW in U0 *after* the fork.
    
    new_secret_key = "Future_Prediction"
    new_secret_val = "The Butler Did It"
    print(f"Storing NEW secret in U0 (Post-Fork): {new_secret_val}")
    mv.memories[0].store(new_secret_key, new_secret_val)
    
    # Check U1 (Should not have it locally)
    local_retrieval = mv.memories[1].retrieve(new_secret_key)
    print(f"U1 Local Retrieval (Control): {local_retrieval}") 
    
    # Attempt Leakage
    leaked_val_1 = mv.leak_memory(0, 1, new_secret_key)
    print(f"U1 Leaked Retrieval: {leaked_val_1}")
    
    print("\n--- Testing Leakage from U0 to U2 (Dissonant) ---")
    leaked_val_2 = mv.leak_memory(0, 2, new_secret_key)
    print(f"U2 Leaked Retrieval: {leaked_val_2}")
    
    # Results
    success = (leaked_val_1 == new_secret_val) and (leaked_val_2 is None)
    status = "SUCCESS" if success else "FAILURE"
    print(f"\nStatus: {status}")
    
    # Save
    output_path = "experiments/results/cycle2292_memory_leakage.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2292,
            "leakage_resonant": leaked_val_1,
            "leakage_dissonant": leaked_val_2,
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
