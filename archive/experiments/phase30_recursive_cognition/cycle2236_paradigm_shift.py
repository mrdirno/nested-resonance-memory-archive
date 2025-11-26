
import sys
import os
import numpy as np
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, SemanticRule, Episode

class AdaptiveCompressor(EpisodicCompressor):
    def monitor_anomaly(self, context: np.ndarray, outcome: float) -> float:
        """
        Check if observation matches prediction. Returns error.
        """
        prediction = self.query_knowledge(context)
        error = abs(prediction - outcome)
        return error

    def prune_rules(self, error_threshold: float = 1.0):
        """
        If a rule is consistently wrong (based on recent episodes), flag it.
        For this simulation, we'll just check if recent episodes contradict rules.
        """
        # Simplified: If we have new episodes that cluster with an old rule but have different outcome
        # We should split or update the rule.
        # Let's just re-compress EVERYTHING (Old Rules + New Episodes) -> Re-crystallization.
        
        # Convert existing rules back to pseudo-episodes (centroids)
        for rule in self.semantic_rules:
            self.episodes.append(Episode(
                id=f"legacy_{rule.id}",
                content=np.zeros(1),
                outcome=rule.average_outcome,
                context=rule.pattern_centroid
            ))
        
        self.semantic_rules = [] # Clear rules
        self.compress() # Re-derive truth

def run_paradigm_shift():
    print("MOG ONLINE: Cycle 2236 - The Paradigm Shift", flush=True)
    
    compressor = AdaptiveCompressor(similarity_threshold=0.9)
    # 1. Old World: Red is Bad (-1)
    print("Phase 1: Establishing Old Paradigm (Red = Bad)")
    red_context = np.array([1.0, 0.0, 0.0])
    compressor.add_episode(Episode("e1", np.zeros(1), -1.0, red_context))
    compressor.add_episode(Episode("e2", np.zeros(1), -1.0, red_context))
    compressor.compress()
    
    print(f"Rule 0 Outcome: {compressor.semantic_rules[0].average_outcome}")
    
    # 2. The Shift: Red becomes Good (+1)
    print("\nPhase 2: The Shift (Red = Good)")
    new_reality = 1.0
    
    # Experience the anomaly
    error = compressor.monitor_anomaly(red_context, new_reality)
    print(f"Anomaly Detected! Error: {error:.2f}")
    
    if error > 1.5:
        print("Triggering Re-consolidation...")
        # Add conflicting evidence
        for i in range(5):
            compressor.add_episode(Episode(f"new_{i}", np.zeros(1), new_reality, red_context + np.random.normal(0, 0.01, 3)))
            
        compressor.prune_rules()
        
        # Check new rule
        new_rule = compressor.semantic_rules[0] # Should be the updated one
        print(f"New Rule Outcome: {new_rule.average_outcome:.2f}")
        
        if new_rule.average_outcome > 0.5:
            print("SUCCESS: Paradigm Shift complete. System adapted to new reality.")
            return True
        else:
            print("FAILURE: System stuck in old paradigm.")
            return False

if __name__ == "__main__":
    run_paradigm_shift()
