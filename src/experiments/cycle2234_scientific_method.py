
import sys
import os
import numpy as np
import random
from typing import List, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, Episode, SemanticRule

class Scientist:
    def __init__(self, compressor: EpisodicCompressor):
        self.compressor = compressor
        
    def generate_hypothesis(self) -> np.ndarray:
        """
        Find a region of the state space with low confidence or no rules.
        Simplified: Randomly sample until we find something far from known rules.
        """
        for _ in range(100):
            candidate = np.random.rand(3) # Random context
            # Check distance to known rules
            min_dist = float('inf')
            for rule in self.compressor.semantic_rules:
                dist = np.linalg.norm(candidate - rule.pattern_centroid)
                if dist < min_dist: min_dist = dist
            
            if min_dist > 0.5: # New territory
                return candidate
        return np.random.rand(3) # Fallback

    def conduct_experiment(self, context: np.ndarray) -> Episode:
        """
        Simulate running an experiment in the environment.
        Ground Truth: 
        - Red (1,0,0) -> Bad
        - Green (0,1,0) -> Good
        - Blue (0,0,1) -> Neutral (0.0)
        """
        # Distance to ground truths
        d_red = np.linalg.norm(context - np.array([1,0,0]))
        d_green = np.linalg.norm(context - np.array([0,1,0]))
        d_blue = np.linalg.norm(context - np.array([0,0,1]))
        
        outcome = 0.0
        if d_red < 0.5: outcome = -1.0
        elif d_green < 0.5: outcome = 1.0
        elif d_blue < 0.5: outcome = 0.0 # Blue is neutral
        
        # Noise
        outcome += random.gauss(0, 0.05)
        
        return Episode(
            id=f"exp_{random.randint(0,9999)}",
            content=np.zeros(1),
            outcome=outcome,
            context=context
        )

def run_science_experiment():
    print("MOG ONLINE: Cycle 2234 - The Scientific Method", flush=True)
    
    compressor = EpisodicCompressor(similarity_threshold=0.8)
    # Pre-load Red/Green knowledge
    compressor.semantic_rules.append(SemanticRule("r_red", np.array([1,0,0]), -1.0, 1.0, 10))
    compressor.semantic_rules.append(SemanticRule("r_green", np.array([0,1,0]), 1.0, 1.0, 10))
    
    scientist = Scientist(compressor)
    
    print("Generating Hypothesis (Seeking Unknown)...")
    hypothesis_ctx = scientist.generate_hypothesis()
    print(f"Hypothesis Context: {hypothesis_ctx}")
    
    print("Conducting Experiment...")
    result = scientist.conduct_experiment(hypothesis_ctx)
    print(f"Result Outcome: {result.outcome:.2f}")
    
    print("Updating Knowledge...")
    compressor.add_episode(result)
    compressor.compress() # Should form a new rule if enough data, or just store it
    
    # Check if we learned anything about Blue (if we hit it)
    # Or just check that we have a new episode stored
    # Since we only ran 1 exp, compressor won't form a rule (needs 2).
    # But we should see it in episodes list if not compressed, or...
    # Wait, compress() clears episodes. 
    # Let's run 2 experiments to force a rule.
    
    result2 = scientist.conduct_experiment(hypothesis_ctx + np.array([0.01, 0, 0]))
    compressor.add_episode(result2)
    compressor.compress()
    
    print(f"Total Rules: {len(compressor.semantic_rules)}")
    if len(compressor.semantic_rules) > 2:
        print("SUCCESS: New scientific rule discovered.")
        return True
    else:
        print("FAILURE: No new knowledge formed.")
        return False

if __name__ == "__main__":
    run_science_experiment()
