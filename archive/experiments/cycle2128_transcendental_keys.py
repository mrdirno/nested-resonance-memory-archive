"""
Cycle 2128: Transcendental Keys
================================
Can we use Pi, e, and Phi as the basis for our Codebook?

From C2127: Small codebooks (N=10) are sufficient.
Hypothesis: Using transcendental numbers (Pi, e, Phi) to generate the phases
provides a "Universal Key" that is deterministic, shared, yet non-repeating.

Design:
- Keys: Phases derived from digits of Pi, e, Phi.
- Random: Standard random phases.
- Task: Orthogonality Check (Dot product distribution).
- Goal: Prove Transcendental Keys are as orthogonal as Random Keys.
"""

import numpy as np
import json
from datetime import datetime
import math

class TranscendentalKeys:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 1000 # Pairwise comparisons

    def _normalize(self, v):
        return v / (np.abs(v) + 1e-10)

    def _generate_random(self):
        phases = np.random.uniform(0, 2 * np.pi, self.dimension)
        return np.exp(1j * phases)

    def _generate_transcendental(self, seed_val, offset):
        # Use a simple generator to simulate digits of transcendental numbers
        # Ideally we'd read a file, but for this test we'll use a PRNG seeded 
        # with the transcendental value to simulate the property of "deterministic chaos"
        # Wait, let's try to be more authentic. 
        # Let's use the fractional part of (seed * n)
        
        indices = np.arange(offset, offset + self.dimension)
        # Property: n * irrational mod 1 is uniformly distributed
        phases = (indices * seed_val) % 1.0 * 2 * np.pi
        return np.exp(1j * phases)

    def run_experiment(self):
        results = {"distributions": {}}
        
        # 1. Random vs Random
        sims_rand = []
        for _ in range(self.num_trials):
            v1 = self._generate_random()
            v2 = self._generate_random()
            sim = np.abs(np.vdot(v1, v2)) / self.dimension
            sims_rand.append(sim)
            
        results["distributions"]["random"] = {
            "mean": float(np.mean(sims_rand)),
            "std": float(np.std(sims_rand)),
            "max": float(np.max(sims_rand))
        }
        
        # 2. Transcendental vs Transcendental (Same Seed, Different Offset)
        # This tests if the sequence is self-correlated
        sims_pi = []
        pi_val = np.pi
        for i in range(self.num_trials):
            v1 = self._generate_transcendental(pi_val, i * 1000)
            v2 = self._generate_transcendental(pi_val, (i+1) * 1000)
            sim = np.abs(np.vdot(v1, v2)) / self.dimension
            sims_pi.append(sim)
            
        results["distributions"]["pi_self"] = {
            "mean": float(np.mean(sims_pi)),
            "std": float(np.std(sims_pi)),
            "max": float(np.max(sims_pi))
        }
        
        # 3. Pi vs Phi (Cross-Correlation)
        sims_cross = []
        phi_val = (1 + np.sqrt(5)) / 2
        for i in range(self.num_trials):
            v1 = self._generate_transcendental(pi_val, i * 1000)
            v2 = self._generate_transcendental(phi_val, i * 1000)
            sim = np.abs(np.vdot(v1, v2)) / self.dimension
            sims_cross.append(sim)
            
        results["distributions"]["pi_phi"] = {
            "mean": float(np.mean(sims_cross)),
            "std": float(np.std(sims_cross)),
            "max": float(np.max(sims_cross))
        }
        
        print(f"{'Type':<15} {'Mean':<10} {'Std':<10} {'Max':<10}")
        print("-" * 45)
        for k, v in results["distributions"].items():
            print(f"{k:<15} {v['mean']:<10.4f} {v['std']:<10.4f} {v['max']:<10.4f}")
            
        return results

    def analyze(self, results):
        rand = results["distributions"]["random"]
        pi = results["distributions"]["pi_self"]
        cross = results["distributions"]["pi_phi"]
        
        findings = []
        
        # Check if Pi is as random as Random
        # We expect Mean ~ 1/sqrt(D) ~ 0.03 for D=1024
        expected_mean = 1.0 / np.sqrt(self.dimension) # 0.031
        
        findings.append(f"Expected Random Baseline: {expected_mean:.4f}")
        
        if abs(pi["mean"] - rand["mean"]) < 0.01:
            status = "TRANSCENDENTAL_VALIDATED"
            findings.append("Transcendental keys are effectively orthogonal.")
        else:
            status = "CORRELATION_DETECTED"
            findings.append(f"Warning: Pi self-correlation {pi['mean']:.4f} deviates from random {rand['mean']:.4f}")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2128: Transcendental Keys")
    print("Hypothesis: Pi/Phi provide universal orthogonal bases.")
    print("="*60)
    
    exp = TranscendentalKeys()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2128_transcendental_keys.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
