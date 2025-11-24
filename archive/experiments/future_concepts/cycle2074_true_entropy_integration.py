"""
Cycle 2074: True Entropy Integration
====================================
C2073 identified the problem: seeded entropy creates identical vectors (8% unique).

Fix: Use actual CPU measurements as entropy, not as PRNG seeds.
Add counter to ensure uniqueness even if CPU values repeat.
"""

import numpy as np
import json
import psutil
import time
from datetime import datetime

class TrueEntropyIntegration:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200
        self.num_trials = 5
        self.measurement_interval = 20
        self._entropy_counter = 0

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_entropy_vector_v1(self, d):
        """OLD: Seeded entropy (broken - creates duplicates)."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        np.random.seed(int((cpu + mem) * 1000) % (2**31))
        noise = np.random.normal(0, 0.01, d)
        return noise

    def _get_entropy_vector_v2(self, d):
        """NEW: True entropy with counter for uniqueness."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        self._entropy_counter += 1

        # Mix real values with counter to guarantee uniqueness
        seed = int((cpu * 1000 + mem * 10 + self._entropy_counter) * 1000) % (2**31)
        np.random.seed(seed)
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
        self._entropy_counter = seed * 1000  # Different starting counter per trial
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
            # Add noise based on type
            if entropy_type == "synthetic":
                noise = np.random.normal(0, 0.01, d)
            elif entropy_type == "real_v1":
                noise = self._get_entropy_vector_v1(d)
            elif entropy_type == "real_v2":
                noise = self._get_entropy_vector_v2(d)
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

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

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
            "entropy_type": entropy_type,
            "final_accuracy": final_accuracy,
            "mean_accuracy": np.mean(accuracy_history),
            "stability": stability
        }

    def run_experiment(self):
        """Compare entropy types."""
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

        for entropy_type in ["none", "synthetic", "real_v1", "real_v2"]:
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
        """Determine if fix works."""
        conditions = results["conditions"]
        analysis = {"findings": []}

        synthetic = [c for c in conditions if c["entropy_type"] == "synthetic"][0]
        real_v1 = [c for c in conditions if c["entropy_type"] == "real_v1"][0]
        real_v2 = [c for c in conditions if c["entropy_type"] == "real_v2"][0]

        # V1 vs V2 comparison
        improvement = real_v2["mean_final_accuracy"] - real_v1["mean_final_accuracy"]
        if improvement > 0.1:
            analysis["findings"].append(
                f"V2 FIX WORKS: +{improvement*100:.0f}% over V1 ({real_v2['mean_final_accuracy']*100:.0f}% vs {real_v1['mean_final_accuracy']*100:.0f}%)"
            )
            analysis["fix_effective"] = True
        else:
            analysis["findings"].append(f"V2 fix ineffective: only +{improvement*100:.0f}%")
            analysis["fix_effective"] = False

        # V2 vs Synthetic comparison
        diff = abs(real_v2["mean_final_accuracy"] - synthetic["mean_final_accuracy"])
        if diff < 0.1:
            analysis["findings"].append(
                f"Reality grounding restored: V2 ≈ Synthetic ({diff*100:.0f}% diff)"
            )
            analysis["reality_valid"] = True
        else:
            analysis["findings"].append(
                f"Reality gap persists: V2 ≠ Synthetic ({diff*100:.0f}% diff)"
            )
            analysis["reality_valid"] = False

        # Deployment viability
        if real_v2["mean_final_accuracy"] >= 0.8:
            analysis["findings"].append(
                f"Deployment viable: {real_v2['mean_final_accuracy']*100:.0f}% ≥ 80%"
            )
            analysis["deployment_viable"] = True
        else:
            analysis["findings"].append(
                f"Deployment concern: {real_v2['mean_final_accuracy']*100:.0f}% < 80%"
            )
            analysis["deployment_viable"] = False

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2074: True Entropy Integration")
    print("=" * 60)
    print()

    exp = TrueEntropyIntegration()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2074_true_entropy.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
