"""
Cycle 2126: Threshold Retrieval
================================
Can we find items based on "Fuzzy" similarity?

Hypothesis: Phase Resonance allows retrieval even if the probe is only 
partially similar to the stored key.

Design:
- Store N items with random keys.
- Probe with a "Noisy Key" (Phase noise added).
- Measure retrieval strength (Similarity to target).
- Determine the "break point" (Noise level where Sim < 0.1).
"""

import numpy as np
import json
from datetime import datetime

class ThresholdRetrieval:
    def __init__(self):
        self.dimension = 1024
        self.num_items = 100
        self.num_trials = 10
        self.noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0] # Radians

    def _normalize(self, v):
        return v / (np.abs(v) + 1e-10)

    def _generate(self, d):
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def run_trial(self, noise, seed):
        np.random.seed(seed)
        d = self.dimension
        
        # Store items
        items = [self._generate(d) for _ in range(self.num_items)]
        keys = [self._generate(d) for _ in range(self.num_items)]
        
        memory = np.zeros(d, dtype=np.complex128)
        for k, i in zip(keys, items):
            memory += k * i
            
        # Probe with noisy keys
        avg_sim = 0
        for k, target in zip(keys, items):
            # Add phase noise to key
            phase_noise = np.random.uniform(-noise, noise, d)
            noisy_key = k * np.exp(1j * phase_noise)
            
            # Retrieve
            retrieved = memory * np.conjugate(noisy_key)
            
            # Measure similarity to target
            sim = np.abs(np.vdot(retrieved, target)) / np.linalg.norm(retrieved) / np.linalg.norm(target)
            avg_sim += sim
            
        return avg_sim / self.num_items

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Noise (rad)':<12} {'Similarity':<10}")
        print("-" * 25)
        
        for noise in self.noise_levels:
            sims = []
            for t in range(self.num_trials):
                sim = self.run_trial(noise, t*100)
                sims.append(sim)
                
            avg_sim = np.mean(sims)
            
            results["conditions"].append({
                "noise_level": noise,
                "avg_similarity": float(avg_sim)
            })
            
            print(f"{noise:<12} {avg_sim:<10.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        
        # Find breaking point (Sim < 0.1 is random chance for N=100 items in D=1024 roughly)
        # Wait, random chance is 1/sqrt(D) ~ 0.03.
        # Let's say functional threshold is 0.1.
        
        limit = 0
        for c in conds:
            if c["avg_similarity"] >= 0.1:
                limit = c["noise_level"]
            else:
                break
                
        findings = []
        findings.append(f"Retrieval Limit: +/- {limit} radians")
        
        if limit >= 0.5:
            status = "ROBUST"
            findings.append("System tolerates significant key distortion.")
        else:
            status = "FRAGILE"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2126: Threshold Retrieval")
    print("Hypothesis: Fuzzy keys can retrieve clean data.")
    print("="*60)
    
    exp = ThresholdRetrieval()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2126_threshold_retrieval.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
