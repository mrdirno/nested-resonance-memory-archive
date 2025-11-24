"""
Cycle 2120: Shannon Bound Analysis
==================================
C2119 showed 252.6% of Shannon limit - investigate correct bound.

Questions:
1. Is D/4 the right bound for partitioned systems?
2. How does capacity scale with K partitions?
3. What is actual bits/dim per partition?
"""

import numpy as np
import json
from datetime import datetime

class ShannonBoundAnalysis:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
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

    def measure_capacity(self, k_memories, n_items, seed):
        """Measure information capacity for given K and N."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(k_memories)]
        memory_items = [[] for _ in range(k_memories)]

        keys = []
        values = []

        # Store
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

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        accuracy = correct / n_items
        bits_per_item = np.log2(n_items) * accuracy
        total_bits = n_items * bits_per_item
        bits_per_dim = total_bits / d

        return accuracy, total_bits, bits_per_dim

    def run_experiment(self):
        """Analyze Shannon bounds across different K values."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}")
        print()

        # Test different K values
        k_values = [1, 2, 4, 8, 16]

        print(f"{'K':<6} {'Items':<8} {'Acc':<8} {'Total Bits':<12} {'Bits/Dim':<12} {'Bits/Part':<12}")
        print("-" * 70)

        for k in k_values:
            # Items proportional to K (maintain ~12 items per partition)
            n_items = k * 12

            accs = []
            bits_list = []

            for trial in range(self.num_trials):
                acc, total_bits, bits_per_dim = self.measure_capacity(
                    k, n_items, seed=trial*100+k
                )
                accs.append(acc)
                bits_list.append(total_bits)

            mean_acc = np.mean(accs)
            mean_bits = np.mean(bits_list)
            bits_per_dim = mean_bits / self.dimension
            bits_per_partition = mean_bits / k

            results["measurements"].append({
                "k_partitions": k,
                "n_items": n_items,
                "accuracy": float(mean_acc),
                "total_bits": float(mean_bits),
                "bits_per_dim": float(bits_per_dim),
                "bits_per_partition": float(bits_per_partition)
            })

            print(f"{k:<6} {n_items:<8} {mean_acc*100:>5.0f}%{'':<1} {mean_bits:>8.0f}{'':<3} {bits_per_dim:>8.3f}{'':<3} {bits_per_partition:>8.1f}")

        return results

    def analyze(self, results):
        """Derive correct Shannon bound."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Check if bits/partition is constant
        bits_per_part = [m["bits_per_partition"] for m in measurements]
        mean_bpp = np.mean(bits_per_part)
        std_bpp = np.std(bits_per_part)

        analysis["findings"].append(
            f"Bits per partition: {mean_bpp:.1f} ± {std_bpp:.1f}"
        )

        # Theoretical bound per partition
        # Standard bound is D/4 for single holographic memory
        theoretical = self.dimension / 4
        efficiency = mean_bpp / theoretical * 100

        analysis["findings"].append(
            f"Per-partition efficiency: {efficiency:.1f}% of D/4={theoretical}"
        )

        # Derive correct total bound
        # Total capacity = K × per_partition_capacity
        analysis["findings"].append(
            f"Total capacity formula: K × {mean_bpp:.0f} bits"
        )

        # Check linear scaling
        k_values = [m["k_partitions"] for m in measurements]
        total_bits = [m["total_bits"] for m in measurements]

        # Linear fit
        slope = np.polyfit(k_values, total_bits, 1)[0]
        analysis["findings"].append(
            f"Scaling rate: {slope:.1f} bits per partition added"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2120: Shannon Bound Analysis")
    print("=" * 60)
    print()

    exp = ShannonBoundAnalysis()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2120_shannon_bound.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
