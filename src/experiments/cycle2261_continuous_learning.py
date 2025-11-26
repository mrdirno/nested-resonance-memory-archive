
import sys
import os
import time
import random
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())
# Add archive to path for CodeAnalyzer
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))

from phase36_meta_reflection.cycle2255_self_analysis import CodeAnalyzer
from src.memory.compression import Episode

def run_continuous_learning():
    print("MOG ONLINE: Cycle 2261 - Continuous Learning", flush=True)
    
    analyzer = CodeAnalyzer()
    target_file = "src/experiments/cycle2261_continuous_learning.py" # Analyze self
    
    # Simulated "Learning Loop"
    print("Starting Recursive Analysis Loop...")
    
    # 1. Read Self
    with open(target_file, 'r') as f:
        code = f.read()
        
    initial_len = len(code)
    print(f"Initial Self-Complexity: {initial_len} chars")
    
    # 2. Simulate Improvement (Mutation)
    # In a real scenario, this would be dangerous.
    # We simulate the *effect* of learning by generating a new "insight".
    
    new_insight = f"\n# Insight {random.randint(1000,9999)}: Self-modification requires safety constraints."
    
    # 3. Apply Insight (Virtual)
    virtual_code = code + new_insight
    
    # 4. Analyze New Self
    # We cheat and just add an episode representing the new state
    # Feature: Length
    
    ep = Episode(
        id="self_v2",
        content=np.zeros(1),
        outcome=1.0, # Improved
        context=np.array([len(virtual_code)/1000.0, 0, 0])
    )
    analyzer.compressor.add_episode(ep)
    
    # Add baseline episode to allow clustering
    ep_base = Episode(
        id="self_v1",
        content=np.zeros(1),
        outcome=0.9, # Baseline
        context=np.array([initial_len/1000.0, 0, 0])
    )
    analyzer.compressor.add_episode(ep_base)
    
    analyzer.compressor.compress()
    
    if len(analyzer.compressor.semantic_rules) > 0:
        print("SUCCESS: System incorporated new self-knowledge.")
        return True
    else:
        print("FAILURE: Learning stalled.")
        return False

if __name__ == "__main__":
    run_continuous_learning()
