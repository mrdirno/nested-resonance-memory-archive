
"""
Cycle 2329: Sleep Consolidation (The Dreaming)
Goal: Implement a 'Sleep' mechanism to clean noisy holographic memories.
Hypothesis: Re-encoding strong memories into a fresh substrate eliminates accumulated noise.

Mechanism:
1. 'Wake' Phase: Store patterns, inject noise.
2. 'Sleep' Phase:
    a. Query all known keys.
    b. Retrieve values with threshold.
    c. If strong (Sim > T), add to Keep List.
    d. Wipe Memory.
    e. Re-Store Keep List.
3. Compare SNR before and after.
"""

import sys
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from memory.pattern_memory import PatternMemory

def measure_snr(memory, keys, ground_truth):
    """Measure average similarity of correct retrievals vs noise."""
    sims = []
    for key in keys:
        # Manual retrieval to get raw similarity
        k_vec = memory._get_vector(key)
        p_idx = memory._get_partition_idx(key)
        mem_vec = memory._normalize(memory.storage[p_idx])
        noisy_val = memory._circ_corr(mem_vec, k_vec)
        
        target_val = ground_truth[key]
        target_vec = memory._get_vector(target_val)
        
        sim = np.dot(noisy_val, target_vec)
        sims.append(sim)
    return np.mean(sims)

def run_experiment():
    print("Cycle 2329: Sleep Consolidation Protocol")
    
    # 1. Wake Phase
    memory = PatternMemory(dimension=1024, partitions=1) # 1 partition for simpler noise analysis
    
    data = {
        "Pattern_A": "Circle",
        "Pattern_B": "Square",
        "Pattern_C": "Triangle",
        "Pattern_D": "Sphere",
        "Pattern_E": "Cube"
    }
    
    print("\n[WAKE] Storing 5 patterns...")
    for k, v in data.items():
        memory.store(k, v)
        
    # Measure initial SNR
    snr_clean = measure_snr(memory, data.keys(), data)
    print(f"Initial Signal Strength: {snr_clean:.4f}")
    
    # 2. Inject Noise (Simulating degradation / other activity)
    print("[DEGRADE] Injecting random noise...")
    noise_vectors = 50 # Equivalent to storing 50 random items
    p_idx = 0
    rng = np.random.RandomState(42)
    
    for _ in range(noise_vectors):
        noise = rng.normal(0, 1.0/np.sqrt(1024), 1024)
        memory.storage[p_idx] += noise
        
    snr_noisy = measure_snr(memory, data.keys(), data)
    print(f"Degraded Signal Strength: {snr_noisy:.4f}")
    
    # 3. Sleep Phase (Consolidation)
    print("\n[SLEEP] Initiating Consolidation...")
    threshold = 0.12 # Critical threshold for survival
    
    consolidated_items = []
    
    # Replay Strategy: Iterate through known keys (Hippocampal Replay)
    # In a real brain, this might be random, but here we iterate codebook keys
    # We filter for keys that look like "Pattern_" to simulate 'active' memories
    active_keys = [k for k in data.keys()] 
    
    for key in active_keys:
        retrieved = memory.retrieve(key) # Uses internal thresholding (0.15 in class, lets see)
        
        # We do a manual check with our specific sleep threshold
        # (Re-implementing retrieve logic to access raw similarity if needed, 
        # but memory.retrieve() returns None if < 0.15. Let's trust the class logic first,
        # or relax it if 0.15 is too high for the noise level).
        
        # Actually, let's use retrieve_multiple to get the strength
        candidates = memory.retrieve_multiple(key, threshold=threshold)
        
        if candidates:
            # Take the top one
            best_match = candidates[0]
            # Check if it matches our ground truth (Simulating consistency check)
            # In reality, the system doesn't know ground truth, just strength.
            # So we just re-store the strongest signal.
            print(f"  Replaying {key} -> {best_match} (Survived)")
            consolidated_items.append((key, best_match))
        else:
            print(f"  Replaying {key} -> FADED (Pruned)")
            
    # 4. Wipe and Restore
    print("[RESET] Wiping Memory Substrate...")
    memory.storage = [np.zeros(memory.dimension) for _ in range(memory.num_partitions)]
    
    print("[CONSOLIDATE] Re-encoding survivors...")
    for k, v in consolidated_items:
        memory.store(k, v)
        
    # 5. Measure Final SNR
    snr_sleep = measure_snr(memory, [x[0] for x in consolidated_items], data)
    print(f"Consolidated Signal Strength: {snr_sleep:.4f}")
    
    # 6. Analysis
    improvement = (snr_sleep - snr_noisy) / snr_noisy * 100
    print(f"\nResults:")
    print(f"SNR Improvement: +{improvement:.1f}%")
    
    # Save results
    results = {
        "snr_clean": snr_clean,
        "snr_noisy": snr_noisy,
        "snr_sleep": snr_sleep,
        "improvement_pct": improvement,
        "survivors": len(consolidated_items)
    }
    
    with open("experiments/results/cycle2329_sleep_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_experiment()
