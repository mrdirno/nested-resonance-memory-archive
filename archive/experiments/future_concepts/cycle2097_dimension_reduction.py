"""
Cycle 2097: Dimension Reduction with Partitioning
=================================================
Each partition holds only ~12 items.
C2092 showed N_op = 3.727 × D^0.20 for single memory.

Question: Can we use smaller D in partitioned system?
This would reduce total memory: K × D_small < D_large

Test: 100 items with K=8, varying D.
"""

import numpy as np
import json
from datetime import datetime

class DimensionReductionTest:
    def __init__(self):
        self.num_trials = 3
        self.target_items = 100
        self.k_memories = 8
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _hash_key(self, key, k_memories):
        return int(abs(key[0]) * 1000) % k_memories

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_partitioned(self, d, seed):
        """Run with K partitioned memories at dimension D."""
        np.random.seed(seed)

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        for _ in range(self.target_items):
            key = self._generate(d)
            value = self._generate(d)

            mem_idx = self._hash_key(key, self.k_memories)
            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Operation cycles
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if len(memory_items[mem_idx]) > 0:
                    noise = np.random.normal(0, 0.01, d)
                    memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                    items = memory_items[mem_idx]
                    item_idx = cycle % len(items)
                    key, value = items[item_idx]
                    binding = self._circ_conv(key, value)
                    memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / self.target_items

    def run_experiment(self):
        """Test various dimensions with K=8."""
        results = {
            "metadata": {
                "target_items": self.target_items,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "dimensions": []
        }

        print(f"Target: {self.target_items} items, K={self.k_memories} memories")
        print()
        print(f"{'D':<10} {'Total Mem':<12} {'Accuracy':<12} {'Mem/Single':<12}")
        print("-" * 50)

        baseline_mem = 1024  # Reference single memory size

        for d in [128, 256, 512, 1024, 2048]:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_partitioned(d, seed=trial*100+d)
                accs.append(acc)

            mean_acc = np.mean(accs)
            total_mem = self.k_memories * d
            mem_ratio = total_mem / baseline_mem

            results["dimensions"].append({
                "d": d,
                "total_memory": total_mem,
                "accuracy": float(mean_acc),
                "memory_ratio": float(mem_ratio)
            })

            print(f"{d:<10} {total_mem:<12} {mean_acc*100:>5.0f}%{'':<6} {mem_ratio:.1f}×")

        return results

    def analyze(self, results):
        """Find optimal dimension."""
        dims = results["dimensions"]
        analysis = {"findings": []}

        # Find minimum D for 80% accuracy
        for d in dims:
            if d["accuracy"] >= 0.8:
                analysis["findings"].append(
                    f"Minimum D for 80%: {d['d']} (total={d['total_memory']})"
                )
                analysis["min_d_80"] = d["d"]
                break

        # Compare to single memory baseline
        single_baseline = 1024  # Single memory at D=1024 for ~16 items

        # Efficiency comparison
        if "min_d_80" in analysis:
            min_d = analysis["min_d_80"]
            total = self.k_memories * min_d
            efficiency = self.target_items / total * 1000  # items per 1000 dims
            analysis["findings"].append(
                f"Efficiency: {efficiency:.1f} items per 1000 dims"
            )

        # Memory savings
        best_80 = [d for d in dims if d["accuracy"] >= 0.8]
        if best_80:
            smallest = min(best_80, key=lambda x: x["total_memory"])
            if smallest["total_memory"] < single_baseline:
                savings = (1 - smallest["total_memory"]/single_baseline) * 100
                analysis["findings"].append(
                    f"Memory savings: {savings:.0f}% vs single D=1024"
                )
            else:
                overhead = (smallest["total_memory"]/single_baseline - 1) * 100
                analysis["findings"].append(
                    f"Memory overhead: +{overhead:.0f}% vs single D=1024 (but {self.target_items} vs 16 items)"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2097: Dimension Reduction with Partitioning")
    print("=" * 60)
    print()

    exp = DimensionReductionTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2097_dimension_reduction.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
