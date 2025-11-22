"""
Cycle 2059: Critical Replenishment Threshold
=============================================
Find minimum replenishment rate needed for survival at each load level.

From C2058: Replenishment delays but cannot prevent collapse.
Question: What is the minimum rate R_crit(L) to maintain >50% accuracy?

This establishes the "economics of memory maintenance" - how much effort
is required to keep memories alive at different capacity utilizations.
"""

import numpy as np
import json
from datetime import datetime

class CriticalReplenishmentThreshold:
    def __init__(self):
        self.dimension = 1024
        self.n_crit = int(0.042 * self.dimension)
        self.phi = (1 + np.sqrt(5)) / 2
        self.num_cycles = 300
        self.num_trials = 5
        self.survival_threshold = 0.5  # Minimum retention ratio

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _store_items(self, n_items):
        d = self.dimension
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

        return memory, keys, values

    def _recall_accuracy(self, memory, keys, values):
        correct = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._normalize(self._circ_conv(memory, key_inv))
            similarity = np.dot(retrieved, value)
            if similarity > 0.1:
                correct += 1
        return correct / len(keys) if keys else 0

    def test_survival(self, load_fraction, replenish_rate, seed):
        """Test if system survives with given parameters."""
        np.random.seed(seed)

        n_items = max(1, int(load_fraction * self.n_crit))
        d = self.dimension

        memory, keys, values = self._store_items(n_items)
        initial_accuracy = self._recall_accuracy(memory, keys, values)

        if initial_accuracy == 0:
            return False, 0

        comp_prob = 0.1 * self.phi
        decomp_prob = 0.1 / self.phi

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

            # Replenishment
            if replenish_rate > 0 and np.random.random() < replenish_rate:
                idx = np.random.randint(len(keys))
                binding = self._circ_conv(keys[idx], values[idx])
                memory = self._normalize(memory + 0.5 * binding)

        final_accuracy = self._recall_accuracy(memory, keys, values)
        retention = final_accuracy / initial_accuracy if initial_accuracy > 0 else 0

        survived = retention >= self.survival_threshold
        return survived, retention

    def find_critical_threshold(self, load_fraction):
        """Binary search for critical replenishment rate."""
        low = 0.0
        high = 0.5

        # Verify bounds
        all_dead = all(not self.test_survival(load_fraction, low, seed)[0]
                      for seed in range(self.num_trials))
        any_alive = any(self.test_survival(load_fraction, high, seed)[0]
                       for seed in range(self.num_trials))

        if not all_dead:
            return 0.0  # No replenishment needed
        if not any_alive:
            return -1.0  # Cannot survive even with max replenishment

        # Binary search
        for _ in range(10):
            mid = (low + high) / 2
            survival_rate = sum(self.test_survival(load_fraction, mid, seed)[0]
                               for seed in range(self.num_trials)) / self.num_trials

            if survival_rate >= 0.5:  # Majority survive
                high = mid
            else:
                low = mid

        return (low + high) / 2

    def run_experiment(self):
        """Find critical thresholds for all load levels."""
        load_fractions = [0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_crit": self.n_crit,
                "phi": self.phi,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "survival_threshold": self.survival_threshold,
                "timestamp": datetime.now().isoformat()
            },
            "thresholds": []
        }

        print(f"{'Load':<10} {'N Items':<10} {'R_crit':<10} {'Status':<20}")
        print("-" * 50)

        for load in load_fractions:
            n_items = int(load * self.n_crit)
            r_crit = self.find_critical_threshold(load)

            if r_crit < 0:
                status = "IMPOSSIBLE"
            elif r_crit == 0:
                status = "NO REPLENISH NEEDED"
            else:
                status = f"R_crit = {r_crit:.4f}"

            results["thresholds"].append({
                "load_fraction": load,
                "n_items": n_items,
                "r_critical": r_crit,
                "status": status
            })

            print(f"{load*100:<10.0f}% {n_items:<10} {r_crit:<10.4f} {status:<20}")

        return results

    def analyze(self, results):
        """Analyze scaling of critical threshold."""
        thresholds = results["thresholds"]

        # Filter valid thresholds
        valid = [(t["load_fraction"], t["r_critical"])
                 for t in thresholds if t["r_critical"] > 0]

        if len(valid) < 2:
            return {"status": "INSUFFICIENT_DATA"}

        loads = np.array([v[0] for v in valid])
        rates = np.array([v[1] for v in valid])

        # Test exponential scaling: R_crit = a * exp(b * L)
        log_rates = np.log(rates + 1e-10)
        coeffs = np.polyfit(loads, log_rates, 1)
        r_squared = 1 - np.sum((log_rates - np.polyval(coeffs, loads))**2) / \
                       np.sum((log_rates - np.mean(log_rates))**2)

        analysis = {
            "scaling_model": "exponential",
            "exponent": float(coeffs[0]),
            "base_rate": float(np.exp(coeffs[1])),
            "r_squared": float(r_squared),
            "equation": f"R_crit ≈ {np.exp(coeffs[1]):.4f} × exp({coeffs[0]:.2f} × L)"
        }

        if r_squared > 0.8:
            analysis["finding"] = f"EXPONENTIAL SCALING CONFIRMED (R²={r_squared:.3f})"
        else:
            analysis["finding"] = f"Non-exponential relationship (R²={r_squared:.3f})"

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2059: Critical Replenishment Threshold")
    print("=" * 60)
    print()

    exp = CriticalReplenishmentThreshold()
    print(f"D={exp.dimension}, N_crit={exp.n_crit}")
    print(f"Finding minimum replenishment for >50% retention")
    print()

    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Scaling: {analysis.get('equation', 'N/A')}")
    print(f"Finding: {analysis.get('finding', 'N/A')}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2059_critical_threshold.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
