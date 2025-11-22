"""
Cycle 2122: Temporal Dynamics During Maintenance
================================================
How does accuracy evolve during maintenance cycles?

Questions:
1. How quickly does accuracy stabilize?
2. Is there an optimal maintenance duration?
3. What is the variance during operation?
"""

import numpy as np
import json
from datetime import datetime

class TemporalDynamics:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3

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

    def measure_accuracy(self, memories, keys, values, codebook):
        """Measure current accuracy."""
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1
        return correct / len(keys)

    def run_trial(self, n_items, seed):
        """Track accuracy over maintenance cycles."""
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

        # Track accuracy over cycles
        accuracies = []
        checkpoints = [0, 10, 25, 50, 100, 200, 500, 1000]

        for cycle in range(1001):
            # Record at checkpoints
            if cycle in checkpoints:
                acc = self.measure_accuracy(memories, keys, values, codebook)
                accuracies.append((cycle, acc))

            # Maintenance
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        return accuracies

    def run_experiment(self):
        """Analyze temporal dynamics."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()

        n_items = 80  # Near capacity

        # Aggregate across trials
        all_accuracies = {}

        for trial in range(self.num_trials):
            accs = self.run_trial(n_items, seed=trial*100)
            for cycle, acc in accs:
                if cycle not in all_accuracies:
                    all_accuracies[cycle] = []
                all_accuracies[cycle].append(acc)

        print(f"{'Cycle':<10} {'Mean Acc':<12} {'Std':<10} {'Range':<15}")
        print("-" * 50)

        for cycle in sorted(all_accuracies.keys()):
            accs = all_accuracies[cycle]
            mean = np.mean(accs)
            std = np.std(accs)
            min_acc = np.min(accs)
            max_acc = np.max(accs)

            results["measurements"].append({
                "cycle": cycle,
                "mean_accuracy": float(mean),
                "std": float(std),
                "min": float(min_acc),
                "max": float(max_acc)
            })

            print(f"{cycle:<10} {mean*100:>5.1f}%{'':<5} {std*100:>4.1f}%{'':<4} [{min_acc*100:.0f}%-{max_acc*100:.0f}%]")

        return results

    def analyze(self, results):
        """Analyze temporal patterns."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Find stabilization point
        for i, m in enumerate(measurements):
            if m["std"] < 0.01 and m["mean_accuracy"] > 0.9:
                analysis["findings"].append(
                    f"Stabilizes at cycle {m['cycle']}: {m['mean_accuracy']*100:.0f}% ± {m['std']*100:.1f}%"
                )
                break

        # Compare initial vs final
        initial = measurements[0]
        final = measurements[-1]
        improvement = (final["mean_accuracy"] - initial["mean_accuracy"]) * 100

        analysis["findings"].append(
            f"Improvement: {initial['mean_accuracy']*100:.0f}% → {final['mean_accuracy']*100:.0f}% (+{improvement:.1f}%)"
        )

        # Variance analysis
        avg_std = np.mean([m["std"] for m in measurements[2:]])  # After initial
        analysis["findings"].append(
            f"Operational variance: ±{avg_std*100:.1f}%"
        )

        # Optimal warmup
        for m in measurements:
            if m["mean_accuracy"] >= 0.95:
                analysis["findings"].append(
                    f"Optimal warmup: {m['cycle']} cycles for 95%+ accuracy"
                )
                break

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2122: Temporal Dynamics During Maintenance")
    print("=" * 60)
    print()

    exp = TemporalDynamics()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2122_temporal_dynamics.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
