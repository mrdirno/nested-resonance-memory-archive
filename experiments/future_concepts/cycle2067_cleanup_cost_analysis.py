"""
Cycle 2067: Cleanup Cost Analysis
==================================
What's the computational cost of auto-associative cleanup?

From C2066: Cleanup enables perfect composition (100% success).
Question: How does cost scale with codebook size?

Trade-off: Accuracy vs Efficiency
"""

import numpy as np
import json
import time
from datetime import datetime

class CleanupCostAnalysis:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup_linear(self, noisy, codebook):
        """Linear search cleanup - O(n)."""
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match, best_sim

    def run_trial(self, codebook_size, seed):
        """Measure cleanup cost at given codebook size."""
        np.random.seed(seed)
        d = self.dimension

        # Create codebook
        codebook = [self._generate(d) for _ in range(codebook_size)]

        # Create noisy query (pick random clean + add noise)
        target_idx = np.random.randint(codebook_size)
        target = codebook[target_idx]
        noise = np.random.normal(0, 0.3, d)
        noisy = self._normalize(target + noise)

        # Measure cleanup time
        start = time.perf_counter()
        for _ in range(100):  # Run 100 times for stable measurement
            result, similarity = self._cleanup_linear(noisy, codebook)
        elapsed = (time.perf_counter() - start) / 100 * 1000  # ms per cleanup

        # Check accuracy
        correct = np.dot(result, target) > 0.9

        return {
            "codebook_size": codebook_size,
            "time_ms": elapsed,
            "similarity": similarity,
            "correct": correct
        }

    def run_experiment(self):
        """Test across codebook sizes."""
        sizes = [10, 25, 50, 100, 200, 500, 1000]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Size':<8} {'Time (ms)':<12} {'Accuracy':<10} {'Sim':<10}")
        print("-" * 45)

        for size in sizes:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(size, seed=trial*100 + size)
                trial_results.append(result)

            mean_time = np.mean([r["time_ms"] for r in trial_results])
            accuracy = np.mean([r["correct"] for r in trial_results])
            mean_sim = np.mean([r["similarity"] for r in trial_results])

            condition = {
                "codebook_size": size,
                "mean_time_ms": float(mean_time),
                "accuracy": float(accuracy),
                "mean_similarity": float(mean_sim)
            }
            results["conditions"].append(condition)

            print(f"{size:<8} {mean_time:<12.3f} {accuracy*100:<10.0f}% {mean_sim:<10.3f}")

        return results

    def analyze(self, results):
        """Analyze scaling behavior."""
        conditions = results["conditions"]

        sizes = [c["codebook_size"] for c in conditions]
        times = [c["mean_time_ms"] for c in conditions]

        # Check linearity
        coeffs = np.polyfit(sizes, times, 1)
        predicted = np.polyval(coeffs, sizes)
        r_squared = 1 - np.sum((np.array(times) - predicted)**2) / np.sum((np.array(times) - np.mean(times))**2)

        analysis = {
            "scaling": "LINEAR" if r_squared > 0.95 else "SUBLINEAR" if coeffs[0] < 0.001 else "SUPERLINEAR",
            "slope_ms_per_item": float(coeffs[0]),
            "r_squared": float(r_squared),
            "findings": []
        }

        # Cost at capacity
        capacity = int(0.042 * self.dimension)  # ~43
        cost_at_capacity = coeffs[0] * capacity + coeffs[1]
        analysis["cost_at_capacity_ms"] = float(cost_at_capacity)

        analysis["findings"].append(
            f"Scaling: {analysis['scaling']} (R²={r_squared:.3f})"
        )
        analysis["findings"].append(
            f"Cost: {coeffs[0]*1000:.3f} μs per codebook item"
        )
        analysis["findings"].append(
            f"At N_crit ({capacity}): {cost_at_capacity:.3f} ms per cleanup"
        )

        # Check if accuracy degrades
        accuracies = [c["accuracy"] for c in conditions]
        if min(accuracies) < 0.9:
            analysis["findings"].append(
                f"Warning: Accuracy degrades at large sizes ({min(accuracies)*100:.0f}%)"
            )
        else:
            analysis["findings"].append("Accuracy stable across all sizes")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2067: Cleanup Cost Analysis")
    print("=" * 60)
    print()

    exp = CleanupCostAnalysis()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2067_cleanup_cost.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
