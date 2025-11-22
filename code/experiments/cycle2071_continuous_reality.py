"""
Cycle 2071: Continuous Reality Integration
===========================================
Test cognition under continuous real entropy stream.

From C2070: Single-shot reality grounding validated.
Question: Does it hold under continuous perturbation?

This simulates actual deployment conditions where the system
experiences ongoing environmental noise, not just initialization noise.
"""

import numpy as np
import json
import psutil
import time
from datetime import datetime

class ContinuousReality:
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

        # Use as seed for structured noise
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

    def run_trial(self, entropy_type, seed):
        """Run continuous operation with given entropy type."""
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

        # Track accuracy over time
        accuracy_history = []

        for cycle in range(self.num_cycles):
            # Add noise based on type
            if entropy_type == "synthetic":
                noise = np.random.normal(0, 0.01, d)
            elif entropy_type == "real":
                noise = self._get_entropy_vector(d)
            else:
                noise = np.zeros(d)

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

            # Hebbian refresh (round-robin)
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

            # Measure accuracy periodically
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

        # Final accuracy
        final_accuracy = accuracy_history[-1] if accuracy_history else 0

        # Stability (variance of accuracy)
        stability = 1 - np.std(accuracy_history) if len(accuracy_history) > 1 else 1

        return {
            "entropy_type": entropy_type,
            "final_accuracy": final_accuracy,
            "mean_accuracy": np.mean(accuracy_history),
            "stability": stability,
            "accuracy_history": accuracy_history
        }

    def run_experiment(self):
        """Compare entropy types under continuous operation."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Entropy':<12} {'Final Acc':<12} {'Mean Acc':<12} {'Stability':<12}")
        print("-" * 50)

        for entropy_type in ["none", "synthetic", "real"]:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(entropy_type, seed=trial*100)
                trial_results.append(result)

            mean_final = np.mean([r["final_accuracy"] for r in trial_results])
            mean_mean = np.mean([r["mean_accuracy"] for r in trial_results])
            mean_stability = np.mean([r["stability"] for r in trial_results])

            condition = {
                "entropy_type": entropy_type,
                "mean_final_accuracy": float(mean_final),
                "mean_accuracy": float(mean_mean),
                "mean_stability": float(mean_stability)
            }
            results["conditions"].append(condition)

            print(f"{entropy_type:<12} {mean_final*100:<12.0f}% {mean_mean*100:<12.0f}% {mean_stability:<12.3f}")

        return results

    def analyze(self, results):
        """Determine if continuous reality is viable."""
        conditions = results["conditions"]

        analysis = {"findings": []}

        synthetic = [c for c in conditions if c["entropy_type"] == "synthetic"][0]
        real = [c for c in conditions if c["entropy_type"] == "real"][0]

        # Accuracy comparison
        acc_diff = abs(synthetic["mean_final_accuracy"] - real["mean_final_accuracy"])
        if acc_diff < 0.1:
            analysis["findings"].append(
                f"Continuous operation: Real ≈ Synthetic ({acc_diff*100:.0f}% diff)"
            )
            analysis["continuous_valid"] = True
        else:
            analysis["findings"].append(
                f"Continuous operation: Real ≠ Synthetic ({acc_diff*100:.0f}% diff)"
            )
            analysis["continuous_valid"] = False

        # Stability comparison
        stab_diff = synthetic["mean_stability"] - real["mean_stability"]
        if abs(stab_diff) < 0.1:
            analysis["findings"].append("Stability: Real ≈ Synthetic")
        elif stab_diff > 0:
            analysis["findings"].append(
                f"Warning: Real less stable than synthetic ({stab_diff:.2f})"
            )

        # Overall viability
        if real["mean_final_accuracy"] >= 0.8:
            analysis["findings"].append(
                "Deployment viable: ≥80% accuracy under continuous real entropy"
            )
        else:
            analysis["findings"].append(
                f"Deployment concern: Only {real['mean_final_accuracy']*100:.0f}% accuracy"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2071: Continuous Reality Integration")
    print("=" * 60)
    print()

    exp = ContinuousReality()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2071_continuous_reality.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
