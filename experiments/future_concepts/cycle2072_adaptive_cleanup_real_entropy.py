"""
Cycle 2072: Adaptive Cleanup for Real Entropy
==============================================
Investigate C2071's deployment concern: 68% accuracy with continuous real entropy.

Hypothesis: Real entropy accumulates differently than synthetic due to:
1. Correlated noise from CPU/memory sampling
2. Non-Gaussian structure
3. Temporal patterns in system metrics

Test: Vary cleanup frequency to compensate for real entropy characteristics.
"""

import numpy as np
import json
import psutil
import time
from datetime import datetime

class AdaptiveCleanupRealEntropy:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200
        self.num_trials = 5
        self.measurement_interval = 20

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_entropy_vector(self, d):
        """Get real entropy as noise vector."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        np.random.seed(int((cpu + mem) * 1000) % (2**31))
        noise = np.random.normal(0, 0.01, d)
        return noise

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, cleanup_freq, seed):
        """Run with specified cleanup frequency."""
        np.random.seed(seed)
        d = self.dimension

        # Create and store patterns
        n_items = 10
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
        accuracy_history = []

        for cycle in range(self.num_cycles):
            # Always use real entropy
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Composition dynamics
            phi = (1 + np.sqrt(5)) / 2
            if np.random.random() < 0.1 * phi:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            if np.random.random() < 0.1 / phi:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

            # Adaptive cleanup based on frequency
            if cleanup_freq > 0 and cycle % cleanup_freq == 0:
                # Clean the memory itself by re-encoding all items
                cleaned_memory = np.zeros(d)
                for key, value in zip(keys, values):
                    key_inv = np.roll(key[::-1], 1)
                    retrieved = self._circ_conv(memory, key_inv)
                    cleaned = self._cleanup(retrieved, codebook)
                    binding = self._circ_conv(key, cleaned)
                    cleaned_memory = self._normalize(cleaned_memory + binding)
                memory = cleaned_memory

            # Measure accuracy
            if cycle % self.measurement_interval == 0:
                correct = 0
                for key, value in zip(keys, values):
                    key_inv = np.roll(key[::-1], 1)
                    retrieved = self._circ_conv(memory, key_inv)
                    retrieved = self._cleanup(retrieved, codebook)
                    if np.dot(retrieved, value) > 0.5:
                        correct += 1
                accuracy = correct / n_items
                accuracy_history.append(accuracy)

        final_accuracy = accuracy_history[-1] if accuracy_history else 0
        stability = 1 - np.std(accuracy_history) if len(accuracy_history) > 1 else 1

        return {
            "cleanup_freq": cleanup_freq,
            "final_accuracy": final_accuracy,
            "mean_accuracy": np.mean(accuracy_history),
            "stability": stability
        }

    def run_experiment(self):
        """Test different cleanup frequencies with real entropy."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Cleanup Freq':<15} {'Final Acc':<12} {'Mean Acc':<12} {'Stability':<12}")
        print("-" * 55)

        # Test frequencies: 0 (none), 50, 20, 10, 5, 2, 1 (every cycle)
        for cleanup_freq in [0, 50, 20, 10, 5, 2, 1]:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(cleanup_freq, seed=trial*100)
                trial_results.append(result)

            mean_final = np.mean([r["final_accuracy"] for r in trial_results])
            mean_mean = np.mean([r["mean_accuracy"] for r in trial_results])
            mean_stability = np.mean([r["stability"] for r in trial_results])

            freq_label = "never" if cleanup_freq == 0 else f"every {cleanup_freq}"
            condition = {
                "cleanup_freq": cleanup_freq,
                "mean_final_accuracy": float(mean_final),
                "mean_accuracy": float(mean_mean),
                "mean_stability": float(mean_stability)
            }
            results["conditions"].append(condition)

            print(f"{freq_label:<15} {mean_final*100:<12.0f}% {mean_mean*100:<12.0f}% {mean_stability:<12.3f}")

        return results

    def analyze(self, results):
        """Determine optimal cleanup frequency for real entropy."""
        conditions = results["conditions"]
        analysis = {"findings": []}

        # Find best frequency
        best = max(conditions, key=lambda c: c["mean_final_accuracy"])
        baseline = [c for c in conditions if c["cleanup_freq"] == 0][0]

        improvement = best["mean_final_accuracy"] - baseline["mean_final_accuracy"]

        if improvement > 0.1:
            freq_label = f"every {best['cleanup_freq']}" if best['cleanup_freq'] > 0 else "never"
            analysis["findings"].append(
                f"Adaptive cleanup effective: {freq_label} achieves {best['mean_final_accuracy']*100:.0f}%"
            )
            analysis["findings"].append(
                f"Improvement over no cleanup: +{improvement*100:.0f}%"
            )
            analysis["adaptive_effective"] = True
        else:
            analysis["findings"].append("Adaptive cleanup ineffective for real entropy")
            analysis["adaptive_effective"] = False

        # Check if we reach deployment threshold (80%)
        if best["mean_final_accuracy"] >= 0.8:
            analysis["findings"].append(
                f"Deployment viable: {best['mean_final_accuracy']*100:.0f}% with optimal cleanup"
            )
            analysis["deployment_viable"] = True
        else:
            analysis["findings"].append(
                f"Deployment concern persists: {best['mean_final_accuracy']*100:.0f}% < 80%"
            )
            analysis["deployment_viable"] = False

        analysis["optimal_frequency"] = best["cleanup_freq"]
        return analysis


def main():
    print("=" * 60)
    print("Cycle 2072: Adaptive Cleanup for Real Entropy")
    print("=" * 60)
    print()

    exp = AdaptiveCleanupRealEntropy()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2072_adaptive_cleanup.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
