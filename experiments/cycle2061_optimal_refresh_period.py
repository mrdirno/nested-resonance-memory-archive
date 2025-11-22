"""
Cycle 2061: Optimal Refresh Period
===================================
Determine how frequently memories need reinforcement.

From C2060: Round-robin beats all strategies.
Question: What's the optimal cycle length for round-robin?

Analogous to DRAM refresh - finding the memory's "decay constant"
and the optimal refresh period to maintain coherence.
"""

import numpy as np
import json
from datetime import datetime

class OptimalRefreshPeriod:
    def __init__(self):
        self.dimension = 1024
        self.n_crit = int(0.042 * self.dimension)
        self.phi = (1 + np.sqrt(5)) / 2
        self.num_cycles = 500
        self.num_trials = 8

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

    def run_trial(self, n_items, refresh_period, seed):
        """Run trial with specified refresh period."""
        np.random.seed(seed)
        d = self.dimension

        memory, keys, values = self._store_items(n_items)
        initial_accuracy = self._recall_accuracy(memory, keys, values)

        if initial_accuracy == 0:
            return {"retention": 0}

        comp_prob = 0.1 * self.phi
        decomp_prob = 0.1 / self.phi

        # Track which item to refresh next (round-robin)
        refresh_idx = 0
        cycles_since_refresh = 0

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

            # Periodic refresh
            cycles_since_refresh += 1
            if cycles_since_refresh >= refresh_period:
                binding = self._circ_conv(keys[refresh_idx], values[refresh_idx])
                memory = self._normalize(memory + 0.5 * binding)
                refresh_idx = (refresh_idx + 1) % len(keys)
                cycles_since_refresh = 0

        final_accuracy = self._recall_accuracy(memory, keys, values)
        retention = final_accuracy / initial_accuracy if initial_accuracy > 0 else 0

        return {
            "initial_accuracy": initial_accuracy,
            "final_accuracy": final_accuracy,
            "retention": retention
        }

    def run_experiment(self):
        """Test different refresh periods."""
        # Load at 75% of N_crit
        n_items = int(0.75 * self.n_crit)

        # Refresh periods to test (cycles between refreshes)
        periods = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_crit": self.n_crit,
                "n_items": n_items,
                "load_fraction": 0.75,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "periods": []
        }

        print(f"Testing refresh periods with {n_items} items (75% load)")
        print()
        print(f"{'Period':<10} {'Retention':<12} {'Final Acc':<12} {'Rate':<10}")
        print("-" * 50)

        for period in periods:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(n_items, period, seed=trial*100)
                trial_results.append(result)

            mean_retention = np.mean([r["retention"] for r in trial_results])
            mean_final = np.mean([r["final_accuracy"] for r in trial_results])
            std_retention = np.std([r["retention"] for r in trial_results])

            # Effective rate: 1 refresh per period cycles
            effective_rate = 1 / period

            period_result = {
                "refresh_period": period,
                "effective_rate": float(effective_rate),
                "mean_retention": float(mean_retention),
                "std_retention": float(std_retention),
                "mean_final_accuracy": float(mean_final)
            }
            results["periods"].append(period_result)

            print(f"{period:<10} {mean_retention:<12.3f} {mean_final:<12.3f} {effective_rate:<10.3f}")

        return results

    def analyze(self, results):
        """Find optimal refresh period."""
        periods = results["periods"]

        # Find best retention
        best = max(periods, key=lambda x: x["mean_retention"])

        # Find efficiency: retention / rate (best bang for buck)
        for p in periods:
            p["efficiency"] = p["mean_retention"] / (p["effective_rate"] + 0.01)

        most_efficient = max(periods, key=lambda x: x["efficiency"])

        analysis = {
            "optimal_period": best["refresh_period"],
            "optimal_retention": best["mean_retention"],
            "optimal_rate": best["effective_rate"],
            "most_efficient_period": most_efficient["refresh_period"],
            "most_efficient_retention": most_efficient["mean_retention"],
            "efficiency_score": most_efficient["efficiency"]
        }

        # Check if there's a phase transition
        retentions = [p["mean_retention"] for p in sorted(periods, key=lambda x: x["refresh_period"])]

        # Find steepest drop
        drops = [retentions[i] - retentions[i+1] for i in range(len(retentions)-1)]
        if drops:
            max_drop_idx = np.argmax(drops)
            analysis["critical_period"] = periods[max_drop_idx + 1]["refresh_period"]
            analysis["max_retention_drop"] = max(drops)

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2061: Optimal Refresh Period")
    print("=" * 60)
    print()

    exp = OptimalRefreshPeriod()

    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Optimal Period: {analysis['optimal_period']} cycles")
    print(f"  → Retention: {analysis['optimal_retention']:.3f}")
    print(f"  → Rate: {analysis['optimal_rate']:.3f}")
    print()
    print(f"Most Efficient Period: {analysis['most_efficient_period']} cycles")
    print(f"  → Retention: {analysis['most_efficient_retention']:.3f}")
    print(f"  → Efficiency Score: {analysis['efficiency_score']:.3f}")

    if "critical_period" in analysis:
        print()
        print(f"Critical Period: {analysis['critical_period']} cycles")
        print(f"  → Max Retention Drop: {analysis['max_retention_drop']:.3f}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2061_refresh_period.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
