"""
Cycle 2077: Stronger Hebbian Signal
===================================
C2076 showed even 30× refresh can't reach 80% at 20 items.

Hypothesis: The 0.5× Hebbian strength is too weak at capacity.
Test stronger signals: 0.5, 1.0, 2.0, 3.0, 5.0
"""

import numpy as np
import json
import psutil
from datetime import datetime

class StrongerHebbianSignal:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200  # 10× ratio for 20 items
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

    def run_trial(self, n_items, hebb_strength, seed):
        """Run with given Hebbian strength."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

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

        # Run cycles
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Hebbian refresh with variable strength
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + hebb_strength * binding)

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
        """Test different Hebbian strengths."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "strengths": []
        }

        n_items = 20

        print(f"Testing with {n_items} items, {self.num_cycles} cycles (10× ratio)")
        print()
        print(f"{'Strength':<12} {'Accuracy':<12}")
        print("-" * 25)

        for strength in [0.5, 1.0, 2.0, 3.0, 5.0]:
            accuracies = []
            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, strength, seed=trial*100+int(strength*10))
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            results["strengths"].append({
                "strength": strength,
                "n_items": n_items,
                "accuracy": mean_acc
            })

            print(f"{strength}×{'':<9} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Find optimal Hebbian strength."""
        strengths = results["strengths"]
        analysis = {"findings": []}

        # Find best strength
        best = max(strengths, key=lambda s: s["accuracy"])
        baseline = [s for s in strengths if s["strength"] == 0.5][0]

        improvement = best["accuracy"] - baseline["accuracy"]

        if improvement > 0.1:
            analysis["findings"].append(
                f"Stronger signal helps: {best['strength']}× achieves {best['accuracy']*100:.0f}% (+{improvement*100:.0f}%)"
            )
        else:
            analysis["findings"].append(
                f"Strength doesn't help much: best {best['strength']}× at {best['accuracy']*100:.0f}%"
            )

        if best["accuracy"] >= 0.8:
            analysis["findings"].append(
                f"80% threshold achieved with {best['strength']}× Hebbian"
            )
            analysis["threshold_met"] = True
        else:
            analysis["findings"].append(
                f"80% not achieved: capacity limitation at 20 items"
            )
            analysis["threshold_met"] = False

        analysis["optimal_strength"] = best["strength"]
        return analysis


def main():
    print("=" * 60)
    print("Cycle 2077: Stronger Hebbian Signal")
    print("=" * 60)
    print()

    exp = StrongerHebbianSignal()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2077_hebbian_strength.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
