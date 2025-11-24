"""
Cycle 2106: Noise Sensitivity Analysis
======================================
Current implementation uses σ=0.01 noise.

Test: How does accuracy vary with noise level?
- σ=0 (no noise)
- σ=0.001 to σ=0.1

This determines operating bounds for noise parameter.
"""

import numpy as np
import json
from datetime import datetime

class NoiseSensitivityTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
        self.num_cycles = 200
        self.n_items = 50

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

    def run_trial(self, noise_sigma, seed):
        """Run with specified noise level."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Maintenance with specified noise
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                mem_items = memory_items[mem_idx]
                if not mem_items:
                    continue

                # Apply noise
                if noise_sigma > 0:
                    noise = np.random.normal(0, noise_sigma, d)
                    memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(mem_items)
                key, value = mem_items[item_idx]
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

        return correct / self.n_items

    def run_experiment(self):
        """Test various noise levels."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "n_items": self.n_items,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "noise_levels": []
        }

        print(f"D={self.dimension}, K={self.k_memories}, {self.n_items} items")
        print()
        print(f"{'Sigma':<12} {'Accuracy':<12}")
        print("-" * 25)

        noise_levels = [0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]

        for sigma in noise_levels:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(sigma, seed=trial*100+int(sigma*1000))
                accs.append(acc)

            mean_acc = np.mean(accs)

            results["noise_levels"].append({
                "sigma": sigma,
                "accuracy": float(mean_acc)
            })

            print(f"{sigma:<12} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Determine noise bounds."""
        levels = results["noise_levels"]
        analysis = {"findings": []}

        # Find optimal noise
        best = max(levels, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Best noise: σ={best['sigma']} ({best['accuracy']*100:.0f}%)"
        )

        # Find 80% threshold
        for i, level in enumerate(levels):
            if level["accuracy"] < 0.8:
                prev = levels[i-1] if i > 0 else level
                analysis["findings"].append(
                    f"80% threshold: σ between {prev['sigma']} and {level['sigma']}"
                )
                break

        # Compare no noise vs optimal
        no_noise = [l for l in levels if l["sigma"] == 0][0]
        if best["sigma"] > 0 and best["accuracy"] > no_noise["accuracy"]:
            analysis["findings"].append(
                f"Noise helps: +{(best['accuracy'] - no_noise['accuracy'])*100:.0f}% vs no noise"
            )
        elif no_noise["accuracy"] >= best["accuracy"]:
            analysis["findings"].append(
                "No noise is optimal or equivalent"
            )

        # Safe operating range
        safe_levels = [l for l in levels if l["accuracy"] >= 0.9]
        if safe_levels:
            max_safe = max(l["sigma"] for l in safe_levels)
            analysis["findings"].append(
                f"Safe range: σ ≤ {max_safe} for 90%+ accuracy"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2106: Noise Sensitivity Analysis")
    print("=" * 60)
    print()

    exp = NoiseSensitivityTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2106_noise_sensitivity.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
