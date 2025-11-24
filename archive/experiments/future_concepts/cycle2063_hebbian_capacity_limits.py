"""
Cycle 2063: Hebbian Capacity Limits
====================================
Find where Hebbian strengthening breaks down.

From C2062: Continuous refresh causes signal amplification (+12.1%).
Question: Does this scale with capacity, or collapse at some limit?

This completes the memory maintenance arc (C2058-C2063).
"""

import numpy as np
import json
from datetime import datetime

class HebbianCapacityLimits:
    def __init__(self):
        self.dimension = 1024
        self.n_crit = int(0.042 * self.dimension)  # ~43 items
        self.num_cycles = 300
        self.num_trials = 5

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_trial(self, n_items, seed):
        """Test Hebbian strengthening at given capacity."""
        np.random.seed(seed)
        d = self.dimension

        # Store items
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

        # Measure initial signal strength
        initial_signals = []
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            signal = np.dot(retrieved, value)
            initial_signals.append(signal)

        initial_mean = np.mean(initial_signals)

        # Run with continuous refresh (period=1)
        phi = (1 + np.sqrt(5)) / 2
        comp_prob = 0.1 * phi
        decomp_prob = 0.1 / phi
        refresh_idx = 0

        for cycle in range(self.num_cycles):
            # Perturbation
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            # Composition
            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            # Decomposition
            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Continuous refresh (round-robin)
            binding = self._circ_conv(keys[refresh_idx], values[refresh_idx])
            memory = self._normalize(memory + 0.5 * binding)
            refresh_idx = (refresh_idx + 1) % len(keys)

        # Measure final signal strength
        final_signals = []
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            signal = np.dot(retrieved, value)
            final_signals.append(signal)

        final_mean = np.mean(final_signals)

        # Calculate metrics
        signal_change = (final_mean - initial_mean) / initial_mean if initial_mean > 0 else 0

        # Recall accuracy
        correct = sum(1 for s in final_signals if s > 0.1)
        accuracy = correct / len(keys) if keys else 0

        return {
            "n_items": n_items,
            "initial_signal": initial_mean,
            "final_signal": final_mean,
            "signal_change": signal_change,
            "accuracy": accuracy,
            "hebbian_active": signal_change > 0  # Did strengthening occur?
        }

    def run_experiment(self):
        """Test across capacity range."""
        # Test from 25% to 150% of N_crit
        load_fractions = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_crit": self.n_crit,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Load':<8} {'N':<6} {'Signal Δ':<12} {'Accuracy':<10} {'Hebbian':<10}")
        print("-" * 50)

        for load in load_fractions:
            n_items = max(1, int(load * self.n_crit))

            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(n_items, seed=trial*100)
                trial_results.append(result)

            mean_change = np.mean([r["signal_change"] for r in trial_results])
            mean_accuracy = np.mean([r["accuracy"] for r in trial_results])
            hebbian_rate = np.mean([r["hebbian_active"] for r in trial_results])

            condition = {
                "load_fraction": load,
                "n_items": n_items,
                "mean_signal_change": float(mean_change),
                "mean_accuracy": float(mean_accuracy),
                "hebbian_success_rate": float(hebbian_rate)
            }
            results["conditions"].append(condition)

            status = "✓" if hebbian_rate > 0.5 else "✗"
            print(f"{load*100:<8.0f}% {n_items:<6} {mean_change*100:<12.1f}% {mean_accuracy:<10.3f} {status:<10}")

        return results

    def analyze(self, results):
        """Find Hebbian capacity limit."""
        conditions = results["conditions"]

        # Find where Hebbian strengthening fails
        hebbian_limit = None
        for c in conditions:
            if c["hebbian_success_rate"] < 0.5:
                hebbian_limit = c["load_fraction"]
                break

        # Find peak strengthening
        peak = max(conditions, key=lambda x: x["mean_signal_change"])

        analysis = {
            "peak_load": peak["load_fraction"],
            "peak_strengthening": peak["mean_signal_change"],
            "hebbian_limit": hebbian_limit,
            "findings": []
        }

        if hebbian_limit:
            analysis["findings"].append(
                f"Hebbian strengthening fails at {hebbian_limit*100:.0f}% load ({int(hebbian_limit * self.n_crit)} items)"
            )
        else:
            analysis["findings"].append("Hebbian strengthening persists across all tested loads")

        analysis["findings"].append(
            f"Peak strengthening at {peak['load_fraction']*100:.0f}% load: +{peak['mean_signal_change']*100:.1f}%"
        )

        # Check for phase transition
        changes = [c["mean_signal_change"] for c in sorted(conditions, key=lambda x: x["load_fraction"])]
        if len(changes) > 1:
            transitions = [changes[i] - changes[i+1] for i in range(len(changes)-1)]
            max_drop = max(transitions) if transitions else 0
            if max_drop > 0.1:
                analysis["findings"].append(f"Sharp transition detected (drop={max_drop*100:.1f}%)")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2063: Hebbian Capacity Limits")
    print("=" * 60)
    print()

    exp = HebbianCapacityLimits()
    print(f"D={exp.dimension}, N_crit={exp.n_crit}")
    print()

    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2063_hebbian_capacity.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
