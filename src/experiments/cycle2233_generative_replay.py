
import sys
import os
import numpy as np
import random
from typing import List

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, Episode, SemanticRule

class GenerativeDreamer:
    def __init__(self, rules: List[SemanticRule]):
        self.rules = rules
        
    def dream(self, n_samples: int = 1) -> List[Episode]:
        """
        Generate synthetic episodes from semantic rules.
        """
        dreams = []
        for _ in range(n_samples):
            # Pick a rule
            if not self.rules: break
            rule = random.choice(self.rules)
            
            # Generate context (Centroid + Noise)
            # Noise scales with inverse confidence? Low confidence = wilder dreams.
            noise_scale = (1.0 - rule.confidence) * 0.5
            noise = np.random.normal(0, noise_scale, rule.pattern_centroid.shape)
            context = rule.pattern_centroid + noise
            
            # Generate outcome (Average + Variance)
            outcome = rule.average_outcome + random.gauss(0, 0.01)
            
            dreams.append(Episode(
                id=f"dream_{random.randint(0,999999)}",
                content=np.zeros(1),
                outcome=outcome,
                context=context
            ))
        return dreams

def run_dream_experiment():
    print("MOG ONLINE: Cycle 2233 - Generative Replay (Dreaming)", flush=True)
    
    # 1. Setup: Learn Rules (Same as C2232)
    compressor = EpisodicCompressor(similarity_threshold=0.9)
    red_context = np.array([1.0, 0.0, 0.0])
    
    # Feed data
    for i in range(5):
        noise = np.random.normal(0, 0.05, 3)
        ctx = red_context + noise
        ep = Episode(id=f"real_{i}", content=np.zeros(1), outcome=-1.0, context=ctx)
        compressor.add_episode(ep)
        
    compressor.compress()
    print(f"Knowledge Base: {len(compressor.semantic_rules)} rules.")
    
    # 2. Dream
    dreamer = GenerativeDreamer(compressor.semantic_rules)
    print("Dreaming 5 new scenarios...")
    dreams = dreamer.dream(5)
    
    for d in dreams:
        # Check if dream resembles reality
        dist = np.linalg.norm(d.context - red_context)
        print(f"Dream Outcome: {d.outcome:.2f}, Distance from Reality: {dist:.4f}")
        
        if dist > 0.5:
            print("FAILURE: Dream too wild (hallucination).")
            return False
            
    print("\nSUCCESS: Dreams are grounded in semantic reality.")
    return True

if __name__ == "__main__":
    run_dream_experiment()
