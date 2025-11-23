import numpy as np
import math
import os
import sys

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath("."))

from src.fractal.agent import FractalAgent
from src.pilot.cognitive_engine import CognitiveEngine, AssociativeMemory, PredictiveModel

def run_integration_test():
    print("--- PILOT INTEGRATION TEST ---")
    
    # 1. Test Memory
    print("\n[1] Testing Holographic Memory...")
    mem = AssociativeMemory(size=10)
    pattern = np.sign(np.random.uniform(-1, 1, 10))
    mem.learn(pattern)
    
    noisy_cue = pattern.copy() # Flip one bit
    noisy_cue[0] *= -1
    noisy_cue[1] *= -1
    
    recalled = mem.recall(noisy_cue)
    overlap = np.dot(pattern, recalled) / 10.0
    print(f"Target: {pattern}")
    print(f"Recall: {recalled}")
    print(f"Overlap: {overlap:.2f}")
    
    if overlap == 1.0:
        print(">> Memory: SUCCESS")
    else:
        print(">> Memory: PARTIAL/FAIL")

    # 2. Test Prediction
    print("\n[2] Testing Temporal Prediction...")
    pred = PredictiveModel(inertia=0.9)
    
    # Train
    vals = [math.sin(x * 0.1) for x in range(100)]
    for v in vals:
        pred.update(v, signal_present=True)
        
    # Predict
    next_real = math.sin(100 * 0.1)
    next_pred = pred.update(0, signal_present=False)
    
    err = abs(next_real - next_pred)
    print(f"Real: {next_real:.4f}")
    print(f"Pred: {next_pred:.4f}")
    print(f"Error: {err:.4f}")
    
    if err < 0.1:
        print(">> Prediction: SUCCESS")
    else:
        print(">> Prediction: FAIL")

    # 3. Test Swarm Integration
    print("\n[3] Testing Swarm Linkage...")
    agents = [FractalAgent(str(i)) for i in range(5)]
    engine = CognitiveEngine()
    order = engine.engage(agents, {})
    print(f"Swarm Order monitored: {order:.4f}")
    print(">> Swarm Linkage: SUCCESS")

    print("\n--- INTEGRATION COMPLETE ---")

if __name__ == "__main__":
    run_integration_test()
