"""
Cycle 2086: Query Robustness
============================
Test how much noise queries can tolerate before retrieval fails.

This simulates real-world scenarios where query keys may be
imperfect or noisy versions of stored keys.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class QueryRobustness:
    def __init__(self):
        self.dimension = 1024
        self.n_items = 10  # Composition-safe limit
        self.num_cycles = 200
        self.num_trials = 5
        self._entropy_counter = 0

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_entropy_vector(self, d):
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        self._entropy_counter += 1
        seed = int((cpu * 1000 + mem * 10 + self._entropy_counter) * 1000) % (2**31)
        np.random.seed(seed)
        return np.random.normal(0, 0.01, d)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def _add_noise_to_key(self, key, noise_level):
        """Add controlled noise to query key."""
        noise = np.random.normal(0, noise_level, len(key))
        noisy_key = key + noise
        return self._normalize(noisy_key)

    def run_trial(self, noise_level, seed):
        """Test retrieval with noisy queries."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Run operation with V2 entropy
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % self.n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Test retrieval with noisy queries
        correct = 0
        for key, value in zip(keys, values):
            # Add noise to the query key
            noisy_key = self._add_noise_to_key(key, noise_level)
            key_inv = np.roll(noisy_key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / self.n_items

    def run_experiment(self):
        """Test different noise levels."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "noise_levels": []
        }

        print(f"Testing query robustness with {self.n_items} items")
        print()
        print(f"{'Noise σ':<12} {'Accuracy':<12}")
        print("-" * 25)

        # Test noise levels from 0 to 1.0
        for noise in [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
            accuracies = []

            for trial in range(self.num_trials):
                acc = self.run_trial(noise, seed=trial*100+int(noise*100))
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            results["noise_levels"].append({
                "noise": noise,
                "accuracy": mean_acc
            })

            print(f"{noise:<12.1f} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Find noise tolerance threshold."""
        levels = results["noise_levels"]
        analysis = {"findings": []}

        # Find threshold where accuracy drops below 80%
        threshold = None
        for level in levels:
            if level["accuracy"] >= 0.8:
                threshold = level["noise"]
            else:
                break

        if threshold is not None:
            analysis["findings"].append(
                f"Noise tolerance: σ ≤ {threshold} for 80% accuracy"
            )
            analysis["noise_threshold"] = threshold
        else:
            analysis["findings"].append("Low noise tolerance detected")

        # Find 50% accuracy threshold
        threshold_50 = None
        for level in levels:
            if level["accuracy"] >= 0.5:
                threshold_50 = level["noise"]

        if threshold_50:
            analysis["findings"].append(
                f"Graceful degradation to σ = {threshold_50}"
            )

        # Check zero noise baseline
        zero_noise = [l for l in levels if l["noise"] == 0][0]
        if zero_noise["accuracy"] >= 0.9:
            analysis["findings"].append(f"Baseline: {zero_noise['accuracy']*100:.0f}% with clean queries")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2086: Query Robustness")
    print("=" * 60)
    print()

    exp = QueryRobustness()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2086_query_robustness.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
