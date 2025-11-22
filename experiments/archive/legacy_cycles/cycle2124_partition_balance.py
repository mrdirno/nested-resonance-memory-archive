"""
Cycle 2124: Partition Balance
==============================
Revisiting Stereopsis with Phase Resonance.

From C2070: Stereopsis (4x256) beat Monolith (1x1024) for vectors.
From C2119: Phase Capacity is ~0.1 items/dim.

Hypothesis: 4x256 Phase spaces (Capacity 4 * 25 = 100) perform
identically to 1x1024 Phase space (Capacity 100) for storage,
BUT provide better robustness to noise.

Design:
- Control: 1x1024 Phase Memory (100 items).
- Test: 4x256 Phase Memories (25 items each).
- Noise: Inject phase noise.
- Metric: Retrieval Accuracy.
"""

import numpy as np
import json
from datetime import datetime

class PartitionBalance:
    def __init__(self):
        self.total_bits = 1024
        self.num_views = 4
        self.dim_per_view = self.total_bits // self.num_views
        self.total_items = 100
        self.num_trials = 10
        self.noise_levels = [0.1, 0.3, 0.5, 0.7]

    def _normalize(self, v):
        return v / (np.abs(v) + 1e-10)

    def _generate(self, d):
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def run_trial(self, partitioned, noise_level, seed):
        np.random.seed(seed)
        
        # Generate Data
        items = [self._generate(self.total_bits) for _ in range(self.total_items)]
        # Note: Items are 1024-dim.
        # If partitioned, we split item into 4 chunks of 256.
        
        keys = [self._generate(self.total_bits) for _ in range(self.total_items)]
        
        if not partitioned:
            # Monolith: 1x1024
            d = self.total_bits
            memory = np.zeros(d, dtype=np.complex128)
            for k, i in zip(keys, items):
                memory += k * i
                
            # Noise
            noise = np.exp(1j * np.random.uniform(-noise_level, noise_level, d))
            memory = self._normalize(memory) * noise # Apply phase noise
            
            # Retrieval
            correct = 0
            for k, target in zip(keys, items):
                retrieved = memory * np.conjugate(k)
                # Sim
                sim = np.abs(np.vdot(retrieved, target)) / d
                if sim > 0.1: correct += 1
                
            return correct / self.total_items
            
        else:
            # Partitioned: 4x256
            d = self.dim_per_view
            memories = [np.zeros(d, dtype=np.complex128) for _ in range(self.num_views)]
            
            # Split items/keys into chunks
            for k, i in zip(keys, items):
                k_chunks = np.array_split(k, self.num_views)
                i_chunks = np.array_split(i, self.num_views)
                
                for v in range(self.num_views):
                    memories[v] += k_chunks[v] * i_chunks[v]
            
            # Noise
            for v in range(self.num_views):
                noise = np.exp(1j * np.random.uniform(-noise_level, noise_level, d))
                memories[v] = self._normalize(memories[v]) * noise
                
            # Retrieval (Consensus)
            correct = 0
            for idx in range(self.total_items):
                k_chunks = np.array_split(keys[idx], self.num_views)
                target_chunks = np.array_split(items[idx], self.num_views)
                
                # Retrieve from each view
                view_sims = []
                for v in range(self.num_views):
                    retrieved = memories[v] * np.conjugate(k_chunks[v])
                    sim = np.abs(np.vdot(retrieved, target_chunks[v])) / d
                    view_sims.append(sim)
                    
                # Consensus: Average Sim
                avg_sim = np.mean(view_sims)
                if avg_sim > 0.1: correct += 1
                
            return correct / self.total_items

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Noise':<8} {'Mono':<10} {'Part':<10} {'Diff':<10}")
        print("""----------------------------------------""")
        
        for noise in self.noise_levels:
            mono_scores = []
            part_scores = []
            
            for t in range(self.num_trials):
                mono_scores.append(self.run_trial(False, noise, t*100))
                part_scores.append(self.run_trial(True, noise, t*100))
                
            avg_mono = np.mean(mono_scores)
            avg_part = np.mean(part_scores)
            diff = avg_part - avg_mono
            
            results["conditions"].append({
                "noise": noise,
                "monolith_acc": float(avg_mono),
                "partition_acc": float(avg_part),
                "difference": float(diff)
            })
            
            print(f"{noise:<8.1f} {avg_mono:<10.3f} {avg_part:<10.3f} {diff:+.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        avg_diff = np.mean([c["difference"] for c in conds])
        
        findings = []
        findings.append(f"Average Difference: {avg_diff:+.3f}")
        
        if abs(avg_diff) < 0.05:
            status = "EQUIVALENT"
            findings.append("Partitioning provides no benefit for Phase Resonance.")
        elif avg_diff > 0:
            status = "PARTITION_SUPERIOR"
            findings.append("Partitioning improves robustness.")
        else:
            status = "MONOLITH_SUPERIOR"
            findings.append("Monolith is more robust.")
            
        return {"status": status, "findings": findings}

def main():
    print("""==================================================""")
    print("Cycle 2124: Partition Balance")
    print("Hypothesis: Partitioned Phase Space > Monolithic.")
    print("""==================================================""")
    
    exp = PartitionBalance()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2124_partition_balance.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
