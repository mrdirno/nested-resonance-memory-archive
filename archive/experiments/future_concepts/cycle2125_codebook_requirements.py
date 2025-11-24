"""
Cycle 2125: Codebook Requirements Analysis
=========================================
The cleanup codebook is critical for accuracy.
How does codebook size/completeness affect retrieval?

Questions:
1. What if codebook is incomplete?
2. Can we use a smaller codebook?
3. What's the minimum codebook requirement?
"""

import numpy as np
import json
from datetime import datetime

class CodebookRequirements:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3
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
        if not codebook:
            return noisy
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, codebook_fraction, seed):
        """Test with incomplete codebook."""
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

        # Create incomplete codebook
        if codebook_fraction >= 1.0:
            codebook = values.copy()
        else:
            codebook_size = int(n_items * codebook_fraction)
            indices = np.random.choice(n_items, codebook_size, replace=False)
            codebook = [values[i] for i in indices]

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
        correct_in_codebook = 0
        in_codebook = 0

        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)

            is_in_codebook = any(np.allclose(value, v) for v in codebook)
            if is_in_codebook:
                in_codebook += 1

            if np.dot(retrieved, value) > 0.5:
                correct += 1
                if is_in_codebook:
                    correct_in_codebook += 1

        accuracy = correct / n_items
        accuracy_in_codebook = correct_in_codebook / in_codebook if in_codebook > 0 else 0

        return accuracy, accuracy_in_codebook, len(codebook)

    def run_experiment(self):
        """Test different codebook fractions."""
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

        n_items = 80

        print(f"D={self.dimension}, K={self.k_memories}, N={n_items}")
        print()
        print(f"{'Codebook %':<12} {'Size':<8} {'Overall':<10} {'In-Codebook':<12}")
        print("-" * 45)

        for fraction in [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]:
            accs = []
            accs_in = []
            sizes = []

            for trial in range(self.num_trials):
                acc, acc_in, size = self.run_trial(n_items, fraction, seed=trial*100)
                accs.append(acc)
                accs_in.append(acc_in)
                sizes.append(size)

            mean_acc = np.mean(accs)
            mean_acc_in = np.mean(accs_in) if fraction > 0 else 0
            mean_size = np.mean(sizes)

            results["measurements"].append({
                "codebook_fraction": fraction,
                "codebook_size": float(mean_size),
                "overall_accuracy": float(mean_acc),
                "in_codebook_accuracy": float(mean_acc_in)
            })

            print(f"{fraction*100:>5.0f}%{'':<5} {mean_size:>5.0f}{'':<2} {mean_acc*100:>5.0f}%{'':<4} {mean_acc_in*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Analyze codebook requirements."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Full vs partial
        full = next((m for m in measurements if m["codebook_fraction"] == 1.0), None)
        half = next((m for m in measurements if m["codebook_fraction"] == 0.6), None)

        if full and half:
            diff = (half["overall_accuracy"] - full["overall_accuracy"]) * 100
            analysis["findings"].append(
                f"60% codebook: {diff:+.0f}% overall accuracy"
            )

        # No codebook
        none = next((m for m in measurements if m["codebook_fraction"] == 0.0), None)
        if none:
            analysis["findings"].append(
                f"No codebook: {none['overall_accuracy']*100:.0f}% (raw retrieval)"
            )

        # In-codebook accuracy
        for m in measurements:
            if 0 < m["codebook_fraction"] < 1.0:
                if m["in_codebook_accuracy"] > 0.9:
                    analysis["findings"].append(
                        f"At {m['codebook_fraction']*100:.0f}%: {m['in_codebook_accuracy']*100:.0f}% for items in codebook"
                    )
                    break

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2125: Codebook Requirements Analysis")
    print("=" * 60)
    print()

    exp = CodebookRequirements()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2125_codebook_requirements.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
