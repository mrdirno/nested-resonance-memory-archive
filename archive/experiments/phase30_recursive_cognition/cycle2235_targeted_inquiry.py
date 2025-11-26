
import sys
import os
import numpy as np
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, SemanticRule
from src.experiments.cycle2234_scientific_method import Scientist

def run_targeted_inquiry():
    print("MOG ONLINE: Cycle 2235 - Targeted Inquiry", flush=True)
    
    compressor = EpisodicCompressor(similarity_threshold=0.8)
    # Pre-load Red/Green knowledge
    compressor.semantic_rules.append(SemanticRule("r_red", np.array([1,0,0]), -1.0, 1.0, 10))
    compressor.semantic_rules.append(SemanticRule("r_green", np.array([0,1,0]), 1.0, 1.0, 10))
    
    scientist = Scientist(compressor)
    
    # Generate ONE hypothesis
    print("Generating Hypothesis...")
    # Force it to look near Blue for this test, or just use random and stick to it
    # Let's use random but repeat it.
    target_ctx = scientist.generate_hypothesis()
    print(f"Target Context: {target_ctx}")
    
    print("Conducting Batch Experiments (N=5)...")
    for i in range(5):
        # Add slight jitter to simulate real-world variance
        jitter = np.random.normal(0, 0.01, 3)
        result = scientist.conduct_experiment(target_ctx + jitter)
        compressor.add_episode(result)
        
    print("Compressing...")
    compressor.compress()
    
    print(f"Total Rules: {len(compressor.semantic_rules)}")
    for rule in compressor.semantic_rules:
        print(f"Rule {rule.id}: Centroid {rule.pattern_centroid}, Outcome {rule.average_outcome:.2f}")
        
    if len(compressor.semantic_rules) > 2:
        print("SUCCESS: Persistent inquiry created new knowledge.")
        return True
    else:
        print("FAILURE: Still no new rule.")
        return False

if __name__ == "__main__":
    run_targeted_inquiry()
