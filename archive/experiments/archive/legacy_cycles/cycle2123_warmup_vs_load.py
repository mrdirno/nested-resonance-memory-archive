"""
Cycle 2123: Warm-up vs Load
============================
Does "Warming Up" the memory increase capacity?

From C2122: Phase tracks dynamics.
Hypothesis: A memory system that is "spun up" (primed with low-level activity)
can ingest high-load data better than a cold start.

Design:
- Condition A: Cold Start (Store 100 items immediately).
- Condition B: Warm Up (Store 10, then 20, then ... up to 100).
- Metric: Final retrieval accuracy for the 100 items.
"""

import numpy as np
import json
from datetime import datetime

class WarmupVsLoad:
    def __init__(self):
        self.dimension = 1024
        self.total_items = 100
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate(self, d):
        # Use Quaternary Phase (Optimal from C2120)
        phases = np.random.choice([0, np.pi/2, np.pi, 3*np.pi/2], d)
        return np.exp(1j * phases)

    def run_trial(self, warmup, seed):
        np.random.seed(seed)
        d = self.dimension
        
        # Generate all items
        items = [self._generate(d) for _ in range(self.total_items)]
        keys = [self._generate(d) for _ in range(self.total_items)]
        
        memory = np.zeros(d, dtype=np.complex128)
        
        if warmup:
            # Incremental loading (Warm-up)
            # Batch size 10
            batch_size = 10
            for i in range(0, self.total_items, batch_size):
                # Bind batch
                batch_mem = np.zeros(d, dtype=np.complex128)
                for j in range(batch_size):
                    idx = i + j
                    if idx < self.total_items:
                        batch_mem += keys[idx] * items[idx]
                
                # Integrate into main memory
                # Simulate "settling time" or consolidation between batches
                # In phase space, this might mean normalizing or rotating
                # Simple superposition for now
                memory += batch_mem
                # Normalize periodically? No, let amplitude grow to represent strength
        else:
            # Cold Start (All at once)
            for k, i in zip(keys, items):
                memory += k * i
                
        # Retrieval Test (All items)
        correct = 0
        for k, target in zip(keys, items):
            retrieved = memory * np.conjugate(k)
            
            # Check vs random distractor
            sim = np.abs(np.vdot(retrieved, target))
            
            distractor = self._generate(d)
            sim_dist = np.abs(np.vdot(retrieved, distractor))
            
            if sim > sim_dist:
                correct += 1
                
        return correct / self.total_items

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Condition':<12} {'Accuracy':<10}")
        print("-" * 25)
        
        for warmup in [False, True]:
            accs = []
            for t in range(self.num_trials):
                acc = self.run_trial(warmup, t*100)
                accs.append(acc)
                
            avg_acc = np.mean(accs)
            cond_name = "Warm Up" if warmup else "Cold Start"
            
            results["conditions"].append({
                "warmup": warmup,
                "accuracy": float(avg_acc)
            })
            
            print(f"{'cond_name':<12} {avg_acc:<10.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        cold = [c for c in conds if not c["warmup"]][0]
        warm = [c for c in conds if c["warmup"]][0]
        
        diff = warm["accuracy"] - cold["accuracy"]
        
        findings = []
        findings.append(f"Warm Up vs Cold Start Diff: {diff:+.3f}")
        
        # Note: In simple superposition, order shouldn't matter mathematically
        # unless we introduce non-linearity (normalization) between steps.
        # If diff is ~0, it confirms linearity.
        # If diff != 0, something interesting is happening with float precision or logic.
        
        if abs(diff) < 0.01:
            status = "LINEAR_INVARIANT"
            findings.append("Order of ingestion does not affect capacity in linear superposition.")
        elif diff > 0:
            status = "WARMUP_BENEFICIAL"
        else:
            status = "WARMUP_DETRIMENTAL"
            
        return {"status": status, "findings": findings}

def main():
    print("=" * 60)
    print("Cycle 2123: Warm-up vs Load")
    print("Hypothesis: Incremental loading improves capacity.")
    print("=" * 60)
    
    exp = WarmupVsLoad()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2123_warmup_vs_load.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
