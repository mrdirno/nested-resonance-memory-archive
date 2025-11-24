"""
Cycle 2076: Minimum Refresh Ratio
=================================
C2075 showed degradation at 50% N_crit with 100 cycles.

Hypothesis: There's a minimum cycles/items ratio needed.
- C2074: 200 cycles / 10 items = 20 refreshes each → 96%
- C2075: 100 cycles / 21 items = 4.8 refreshes each → 68%

Find the minimum refresh ratio for 80%+ accuracy.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class MinimumRefreshRatio:
    def __init__(self):
        self.dimension = 1024
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
        """V2 entropy with counter."""
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

    def run_trial(self, n_items, refresh_ratio, seed):
        """Run with given items and refresh ratio."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        num_cycles = int(n_items * refresh_ratio)

        # Create and store patterns
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Run cycles with V2 entropy and Hebbian refresh
        for cycle in range(num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Final accuracy
        correct = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_experiment(self):
        """Test different refresh ratios."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "ratios": []
        }

        # Test with 20 items (roughly 50% N_crit)
        n_items = 20

        print(f"Testing with {n_items} items")
        print()
        print(f"{'Ratio':<10} {'Cycles':<10} {'Accuracy':<12}")
        print("-" * 35)

        # Test ratios from 1 to 30 refreshes per item
        for ratio in [1, 2, 3, 5, 7, 10, 15, 20, 30]:
            accuracies = []
            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, ratio, seed=trial*100+ratio)
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            results["ratios"].append({
                "ratio": ratio,
                "n_items": n_items,
                "num_cycles": n_items * ratio,
                "accuracy": mean_acc
            })

            print(f"{ratio}×{'':<7} {n_items * ratio:<10} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Find minimum ratio for 80%+ accuracy."""
        ratios = results["ratios"]
        analysis = {"findings": []}

        # Find threshold
        min_ratio = None
        for r in ratios:
            if r["accuracy"] >= 0.8:
                min_ratio = r["ratio"]
                break

        if min_ratio:
            analysis["findings"].append(
                f"Minimum ratio for 80%: {min_ratio}× (cycles = {min_ratio} × items)"
            )
            analysis["min_ratio_80"] = min_ratio
        else:
            analysis["findings"].append("80% not achieved at tested ratios")

        # Find ratio for 90%
        min_ratio_90 = None
        for r in ratios:
            if r["accuracy"] >= 0.9:
                min_ratio_90 = r["ratio"]
                break

        if min_ratio_90:
            analysis["findings"].append(
                f"Minimum ratio for 90%: {min_ratio_90}×"
            )
            analysis["min_ratio_90"] = min_ratio_90

        # Practical guidance
        if min_ratio:
            analysis["findings"].append(
                f"Deployment rule: Run at least {min_ratio}N cycles for N items"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2076: Minimum Refresh Ratio")
    print("=" * 60)
    print()

    exp = MinimumRefreshRatio()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2076_refresh_ratio.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
