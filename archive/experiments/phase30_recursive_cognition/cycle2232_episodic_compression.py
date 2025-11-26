import sys
import os
import numpy as np
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, Episode

def run_compression_experiment():
    print("MOG ONLINE: Cycle 2232 - Episodic Compression Test", flush=True)
    
    compressor = EpisodicCompressor(similarity_threshold=0.9)
    
    # Generate synthetic episodes
    # Scenario: "Red Light" context -> Bad Outcome
    # Scenario: "Green Light" context -> Good Outcome
    
    red_context = np.array([1.0, 0.0, 0.0])
    green_context = np.array([0.0, 1.0, 0.0])
    
    print("Generating Episodes...", flush=True)
    
    # 10 Red Light episodes (with noise)
    for i in range(10):
        noise = np.random.normal(0, 0.05, 3)
        ctx = red_context + noise
        outcome = -1.0 + random.uniform(-0.1, 0.1)
        ep = Episode(id=f"red_{i}", content=np.zeros(1), outcome=outcome, context=ctx)
        compressor.add_episode(ep)
        
    # 10 Green Light episodes (with noise)
    for i in range(10):
        noise = np.random.normal(0, 0.05, 3)
        ctx = green_context + noise
        outcome = 1.0 + random.uniform(-0.1, 0.1)
        ep = Episode(id=f"green_{i}", content=np.zeros(1), outcome=outcome, context=ctx)
        compressor.add_episode(ep)
        
    print(f"Total Episodes: {len(compressor.episodes)}")
    
    print("Running Compression...", flush=True)
    compressor.compress()
    
    print(f"Generated Rules: {len(compressor.semantic_rules)}")
    for rule in compressor.semantic_rules:
        print(f"Rule {rule.id}: Outcome {rule.average_outcome:.2f}, Conf {rule.confidence:.2f}, Count {rule.count}")
        
    # Verification
    print("\nVerifying Knowledge...")
    
    test_red = red_context + np.array([0.05, 0.05, 0.0])
    pred_red = compressor.query_knowledge(test_red)
    print(f"Query Red Light: Predicted {pred_red:.2f} (Expected < 0)")
    
    test_green = green_context + np.array([0.05, 0.05, 0.0])
    pred_green = compressor.query_knowledge(test_green)
    print(f"Query Green Light: Predicted {pred_green:.2f} (Expected > 0)")
    
    if pred_red < -0.8 and pred_green > 0.8:
        print("\nSUCCESS: Semantic Compression validated.")
        return True
    else:
        print("\nFAILURE: Predictions inaccurate.")
        return False

if __name__ == "__main__":
    run_compression_experiment()
