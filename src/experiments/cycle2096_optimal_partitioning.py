"""
Cycle 2096: Optimal Partitioning Formula
========================================
C2095 showed K memories can hold ~K×16 items.

Derive: For target capacity T, what K is needed?
Test: K = 4, 8, 16, 32 at fixed target of 100 items.

Also test: Does uniform distribution matter?
"""

import numpy as np
import json
from datetime import datetime

class OptimalPartitioningTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.num_cycles = 200
        self.target_items = 100

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

    def run_partitioned(self, n_items, k_memories, seed):
        """Run with K partitioned memories."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(k_memories)]
        memory_items = [[] for _ in range(k_memories)]

        keys = []
        values = []

        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)

            mem_idx = self._hash_key(key, k_memories)
            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Track distribution
        distribution = [len(items) for items in memory_items]

        # Operation cycles
        for cycle in range(self.num_cycles):
            for mem_idx in range(k_memories):
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
            mem_idx = self._hash_key(key, k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items, distribution

    def run_experiment(self):
        """Test various K values for target capacity."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "target_items": self.target_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "partitions": []
        }

        print(f"Target: {self.target_items} items at D={self.dimension}")
        print()
        print(f"{'K':<8} {'Items/K':<10} {'Accuracy':<12} {'Max Load':<10}")
        print("-" * 45)

        for k in [4, 8, 12, 16]:
            accs = []
            max_loads = []

            for trial in range(self.num_trials):
                acc, dist = self.run_partitioned(self.target_items, k, seed=trial*100+k)
                accs.append(acc)
                max_loads.append(max(dist))

            mean_acc = np.mean(accs)
            mean_max_load = np.mean(max_loads)
            expected_per_k = self.target_items / k

            results["partitions"].append({
                "k": k,
                "expected_per_k": float(expected_per_k),
                "accuracy": float(mean_acc),
                "max_load": float(mean_max_load)
            })

            print(f"{k:<8} {expected_per_k:<10.1f} {mean_acc*100:>5.0f}%{'':<6} {mean_max_load:.0f}")

        return results

    def analyze(self, results):
        """Find optimal K."""
        parts = results["partitions"]
        analysis = {"findings": []}

        # Find minimum K for 80% accuracy
        for p in parts:
            if p["accuracy"] >= 0.8:
                analysis["findings"].append(
                    f"K={p['k']} achieves {p['accuracy']*100:.0f}% ({p['expected_per_k']:.0f} items/memory)"
                )
                analysis["min_k_80"] = p["k"]
                break

        # Find minimum K for 90% accuracy
        for p in parts:
            if p["accuracy"] >= 0.9:
                analysis["min_k_90"] = p["k"]
                break

        # Derive formula
        target = results["metadata"]["target_items"]
        if "min_k_80" in analysis:
            k = analysis["min_k_80"]
            per_mem = target / k
            analysis["findings"].append(
                f"Formula: K = ceil(T / {per_mem:.0f}) for 80% accuracy"
            )

        # Check load balancing
        max_imbalance = max(p["max_load"] - p["expected_per_k"] for p in parts)
        if max_imbalance > 5:
            analysis["findings"].append(
                f"Load imbalance: max deviation = {max_imbalance:.0f} items"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2096: Optimal Partitioning Formula")
    print("=" * 60)
    print()

    exp = OptimalPartitioningTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2096_optimal_partitioning.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
