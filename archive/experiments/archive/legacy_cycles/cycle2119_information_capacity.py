"""
Cycle 2119: Information Capacity Scaling
=========================================
Start of The Semantic Frontier Arc.

Objective: Determine the "Vocabulary Size" of Phase Resonance.
How many distinct, orthogonal symbols can we store in D=1024?

Hypothesis: Phase space offers higher capacity than vector space
because we are utilizing the full complex circle, not just hyper-quadrants.

Design:
- Generate N random phase vectors.
- Store them all (superposition).
- Test retrieval of each.
- Find N where accuracy drops below 99%.
"""

import numpy as np
import json
from datetime import datetime

class InformationCapacity:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 5
        self.capacities = [10, 50, 100, 500, 1000, 2000, 5000]

    def _generate_phase_vector(self, d):
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def _phase_multiply(self, a, b):
        return a * b

    def run_trial(self, n_items, seed):
        np.random.seed(seed)
        d = self.dimension
        
        # Generate Vocabulary
        items = [self._generate_phase_vector(d) for _ in range(n_items)]
        keys = [self._generate_phase_vector(d) for _ in range(n_items)]
        
        # Store in Superposition (Sum)
        # Note: For Phase vectors, simple sum works but normalization is tricky.
        # Standard HRR sums and normalizes.
        # For Phase, we sum complex numbers. The result is amplitude + phase.
        # If we discard amplitude (normalize to unit circle), we lose info.
        # Let's try standard superposition: M = sum(key * item)
        
        memory = np.zeros(d, dtype=np.complex128)
        for k, i in zip(keys, items):
            binding = k * i # Phase binding
            memory += binding
            
        # Retrieval
        correct = 0
        for k, target in zip(keys, items):
            # Unbind: M * conjugate(k)
            retrieved_raw = memory * np.conjugate(k)
            
            # The result is (target) + noise.
            # We compare phase alignment.
            
            # Dot product with target
            # If match, real part should be large positive.
            # dot = sum(retrieved_raw * conjugate(target))
            
            # Let's normalize retrieval for fair comparison
            # retrieved_norm = retrieved_raw / (np.abs(retrieved_raw) + 1e-10)
            
            # Similarity metric: coherence
            sim = np.abs(np.vdot(retrieved_raw, target)) / np.linalg.norm(retrieved_raw) / np.linalg.norm(target)
            
            # Check against distractors? Or just raw threshold?
            # Let's check if it's closer to target than a random vector
            distractor = self._generate_phase_vector(d)
            sim_dist = np.abs(np.vdot(retrieved_raw, distractor)) / np.linalg.norm(retrieved_raw) / np.linalg.norm(distractor)
            
            if sim > sim_dist:
                correct += 1
                
        return correct / n_items

    def run_experiment(self):
        results = {"capacities": []}
        
        print(f"{'Items':<10} {'Accuracy':<10}")
        print("-" * 25)
        
        for n in self.capacities:
            accs = []
            for t in range(self.num_trials):
                acc = self.run_trial(n, t*100 + n)
                accs.append(acc)
            
            avg_acc = np.mean(accs)
            results["capacities"].append({
                "n_items": n,
                "accuracy": float(avg_acc)
            })
            
            print(f"{n:<10} {avg_acc:<10.3f}")
            
        return results

    def analyze(self, results):
        caps = results["capacities"]
        
        # Find capacity limit (99% accuracy)
        limit = 0
        for c in caps:
            if c["accuracy"] >= 0.99:
                limit = c["n_items"]
            else:
                break
                
        # Standard HRR Capacity is usually ~0.04 * D (approx 40 items for D=1024)
        # Let's see if Phase beats it.
        
        findings = []
        findings.append(f"Capacity Limit (99%): {limit} items")
        findings.append(f"Capacity/Dimension Ratio: {limit/self.dimension:.3f}")
        
        return {"status": "COMPLETE", "findings": findings}

def main():
    print("="*60)
    print("Cycle 2119: Information Capacity Scaling")
    print("Hypothesis: Phase space > Vector space for storage.")
    print("="*60)
    
    exp = InformationCapacity()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2119_information_capacity.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
