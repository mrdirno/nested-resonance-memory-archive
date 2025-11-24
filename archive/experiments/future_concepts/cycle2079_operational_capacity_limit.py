"""
Cycle 2079: Operational Capacity Limit
=====================================
C2076-C2078 showed 20 items cannot reach 80% regardless of tuning.
C2074 showed 10 items achieves 96%.

Find the actual operational capacity: maximum items for 80%+ accuracy.
This defines the deployable operating range.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class OperationalCapacityLimit:
    def __init__(self):
        self.dimension = 1024
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

    def run_trial(self, n_items, seed):
        """Run standard operation with V2 entropy."""
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

        # Run cycles with V2 entropy and Hebbian refresh
        for cycle in range(self.num_cycles):
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
        """Find operational capacity."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "n_crit": int(0.042 * self.dimension),
                "timestamp": datetime.now().isoformat()
            },
            "capacities": []
        }

        n_crit = int(0.042 * self.dimension)

        print(f"N_crit = {n_crit} (theoretical)")
        print()
        print(f"{'Items':<10} {'% N_crit':<12} {'Accuracy':<12} {'Status':<15}")
        print("-" * 50)

        # Test from 5 to 25 items
        for n_items in [5, 8, 10, 12, 15, 18, 20, 25]:
            accuracies = []
            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, seed=trial*100+n_items)
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            pct_ncrit = n_items / n_crit * 100

            status = "DEPLOYABLE" if mean_acc >= 0.8 else "DEGRADED"
            results["capacities"].append({
                "n_items": n_items,
                "pct_ncrit": pct_ncrit,
                "accuracy": mean_acc
            })

            print(f"{n_items:<10} {pct_ncrit:.0f}%{'':<9} {mean_acc*100:.0f}%{'':<10} {status}")

        return results

    def analyze(self, results):
        """Find operational limits."""
        capacities = results["capacities"]
        analysis = {"findings": []}

        # Find maximum deployable capacity
        deployable = [c for c in capacities if c["accuracy"] >= 0.8]
        if deployable:
            max_deployable = max(deployable, key=lambda c: c["n_items"])
            analysis["findings"].append(
                f"Max deployable: {max_deployable['n_items']} items ({max_deployable['pct_ncrit']:.0f}% N_crit)"
            )
            analysis["max_deployable"] = max_deployable["n_items"]

            # Find where it drops below 80%
            n_crit = results["metadata"]["n_crit"]
            analysis["findings"].append(
                f"Operational range: {max_deployable['pct_ncrit']:.0f}% of theoretical N_crit"
            )
        else:
            analysis["findings"].append("No deployable capacity found at tested items")
            analysis["max_deployable"] = 0

        # Calculate efficiency
        if deployable:
            efficiency = max_deployable["n_items"] / results["metadata"]["n_crit"]
            analysis["findings"].append(
                f"Capacity efficiency: {efficiency*100:.0f}% of theoretical"
            )

        # Scaling insight
        # Find 90% threshold
        high_acc = [c for c in capacities if c["accuracy"] >= 0.9]
        if high_acc:
            max_90 = max(high_acc, key=lambda c: c["n_items"])
            analysis["findings"].append(
                f"90% accuracy limit: {max_90['n_items']} items ({max_90['pct_ncrit']:.0f}% N_crit)"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2079: Operational Capacity Limit")
    print("=" * 60)
    print()

    exp = OperationalCapacityLimit()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2079_operational_capacity.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
