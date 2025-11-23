"""
Cycle 2119: Information Capacity Test
=====================================
How many bits can we reliably store per dimension?

Measure: bits = log2(codebook_size) × retrieval_accuracy
Total bits = items × bits_per_item
Bits per dimension = total_bits / D
"""

import numpy as np
import json
from datetime import datetime

class InformationCapacityTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
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

    def run_trial(self, n_items, seed):
        """Measure information retrieval."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Store
        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
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
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        accuracy = correct / n_items
        return accuracy

    def run_experiment(self):
        """Measure information capacity."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Items':<8} {'Accuracy':<10} {'Bits/Item':<12} {'Total Bits':<12} {'Bits/Dim':<12}")
        print("-" * 60)

        for n_items in [20, 40, 60, 80, 100]:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, seed=trial*100+n_items)
                accs.append(acc)

            mean_acc = np.mean(accs)

            # Information calculation
            # Each value is selected from codebook of n_items
            # Bits per item = log2(n_items) × accuracy
            bits_per_item = np.log2(n_items) * mean_acc
            total_bits = n_items * bits_per_item
            bits_per_dim = total_bits / self.dimension

            results["measurements"].append({
                "n_items": n_items,
                "accuracy": float(mean_acc),
                "bits_per_item": float(bits_per_item),
                "total_bits": float(total_bits),
                "bits_per_dim": float(bits_per_dim)
            })

            print(f"{n_items:<8} {mean_acc*100:>5.0f}%{'':<3} {bits_per_item:>5.2f}{'':<6} {total_bits:>5.0f}{'':<6} {bits_per_dim:>5.3f}")

        return results

    def analyze(self, results):
        """Find maximum information capacity."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Find max bits per dimension
        best = max(measurements, key=lambda x: x["bits_per_dim"])
        analysis["findings"].append(
            f"Peak capacity: {best['bits_per_dim']:.3f} bits/dim at {best['n_items']} items"
        )

        # Compare to theoretical
        # Shannon limit for associative memory is ~D/4 bits
        theoretical = self.dimension / 4
        actual_total = best["total_bits"]
        efficiency = actual_total / theoretical * 100
        analysis["findings"].append(
            f"Efficiency: {efficiency:.1f}% of Shannon limit ({actual_total:.0f}/{theoretical:.0f} bits)"
        )

        # Bits at 80% accuracy
        above_80 = [m for m in measurements if m["accuracy"] >= 0.8]
        if above_80:
            best_80 = max(above_80, key=lambda x: x["total_bits"])
            analysis["findings"].append(
                f"At 80%+ accuracy: {best_80['total_bits']:.0f} bits ({best_80['n_items']} items)"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2119: Information Capacity Test")
    print("=" * 60)
    print()

    exp = InformationCapacityTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2119_information_capacity.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
