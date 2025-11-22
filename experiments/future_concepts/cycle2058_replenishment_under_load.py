"""
Cycle 2058: Replenishment Under Capacity Stress
================================================
Synthesis of C2027 (Phase Transition) + C2057 (Balanced Replenishment).

Hypothesis: Optimal replenishment rate shifts as memory load approaches N_crit.
Key Question: Can replenishment prevent catastrophic phase transition?

Design:
- Load memory to 50%, 75%, 90%, 100% of N_crit
- Test replenishment rates: 0 (baseline), optimal (from C2057), 2x optimal
- Measure: Recall accuracy, time-to-failure, stability
"""

import numpy as np
import json
from datetime import datetime

class ReplenishmentUnderLoad:
    def __init__(self):
        self.dimension = 1024
        self.n_crit = int(0.042 * self.dimension)  # Capacity constant from C2026
        self.phi = (1 + np.sqrt(5)) / 2
        self.num_cycles = 500
        self.num_trials = 5

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _store_items(self, n_items):
        """Store n items and return memory trace + keys for recall test."""
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
        """Test recall accuracy."""
        correct = 0
        for key, value in zip(keys, values):
            # Inverse convolution for retrieval
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._normalize(self._circ_conv(memory, key_inv))
            similarity = np.dot(retrieved, value)
            if similarity > 0.1:  # Threshold for correct recall
                correct += 1
        return correct / len(keys) if keys else 0

    def run_experiment(self, load_fraction, replenish_rate, seed):
        """Run single trial with given load and replenishment."""
        np.random.seed(seed)

        n_items = int(load_fraction * self.n_crit)
        d = self.dimension

        # Initial storage
        memory, keys, values = self._store_items(n_items)
        initial_accuracy = self._recall_accuracy(memory, keys, values)

        # Golden ratio parameters
        comp_prob = 0.1 * self.phi
        decomp_prob = 0.1 / self.phi

        # Run dynamics with replenishment
        accuracies = [initial_accuracy]

        for cycle in range(self.num_cycles):
            # Random perturbation (simulating interference)
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            # Composition (adds interference)
            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            # Decomposition (removes structure)
            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Replenishment: Re-inject original bindings
            if replenish_rate > 0 and np.random.random() < replenish_rate:
                idx = np.random.randint(len(keys))
                binding = self._circ_conv(keys[idx], values[idx])
                memory = self._normalize(memory + 0.5 * binding)

            # Measure accuracy periodically
            if cycle % 50 == 0:
                acc = self._recall_accuracy(memory, keys, values)
                accuracies.append(acc)

        final_accuracy = self._recall_accuracy(memory, keys, values)

        # Time to 50% degradation
        time_to_failure = self.num_cycles
        for i, acc in enumerate(accuracies):
            if acc < 0.5 * initial_accuracy:
                time_to_failure = i * 50
                break

        return {
            "initial_accuracy": initial_accuracy,
            "final_accuracy": final_accuracy,
            "accuracy_trajectory": accuracies,
            "time_to_failure": time_to_failure,
            "stability": np.mean(accuracies)
        }

    def run_all_conditions(self):
        """Run all experimental conditions."""
        load_fractions = [0.5, 0.75, 0.9, 1.0]
        replenish_rates = [0.0, 0.05, 0.1]  # None, moderate, high

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_crit": self.n_crit,
                "phi": self.phi,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        for load in load_fractions:
            for rate in replenish_rates:
                condition_results = []
                for trial in range(self.num_trials):
                    result = self.run_experiment(load, rate, seed=trial*100)
                    condition_results.append(result)

                # Aggregate
                mean_initial = np.mean([r["initial_accuracy"] for r in condition_results])
                mean_final = np.mean([r["final_accuracy"] for r in condition_results])
                mean_ttf = np.mean([r["time_to_failure"] for r in condition_results])
                mean_stability = np.mean([r["stability"] for r in condition_results])

                condition = {
                    "load_fraction": load,
                    "n_items": int(load * self.n_crit),
                    "replenish_rate": rate,
                    "mean_initial_accuracy": float(mean_initial),
                    "mean_final_accuracy": float(mean_final),
                    "mean_time_to_failure": float(mean_ttf),
                    "mean_stability": float(mean_stability),
                    "retention_ratio": float(mean_final / mean_initial) if mean_initial > 0 else 0
                }
                results["conditions"].append(condition)

                print(f"Load {load*100:.0f}% | Rate {rate:.2f} | "
                      f"Initial {mean_initial:.3f} → Final {mean_final:.3f} | "
                      f"TTF {mean_ttf:.0f}")

        return results

    def analyze(self, results):
        """Analyze results for key insights."""
        conditions = results["conditions"]

        # Find if replenishment prevents phase transition
        analysis = {
            "key_findings": [],
            "hypothesis_status": "UNKNOWN"
        }

        # Compare retention at 100% load with different replenishment
        load_100 = [c for c in conditions if c["load_fraction"] == 1.0]
        no_replenish = [c for c in load_100 if c["replenish_rate"] == 0][0]
        high_replenish = [c for c in load_100 if c["replenish_rate"] == 0.1][0]

        retention_gain = high_replenish["retention_ratio"] - no_replenish["retention_ratio"]

        if retention_gain > 0.1:
            analysis["key_findings"].append(
                f"Replenishment prevents collapse: {retention_gain*100:.1f}% retention gain at N_crit"
            )
            analysis["hypothesis_status"] = "CONFIRMED"
        else:
            analysis["key_findings"].append(
                f"Replenishment insufficient: Only {retention_gain*100:.1f}% retention gain"
            )
            analysis["hypothesis_status"] = "FALSIFIED"

        # Check if optimal rate shifts with load
        for rate in [0.05, 0.1]:
            retentions = [(c["load_fraction"], c["retention_ratio"])
                          for c in conditions if c["replenish_rate"] == rate]
            trend = np.corrcoef([r[0] for r in retentions], [r[1] for r in retentions])[0,1]
            analysis["key_findings"].append(
                f"Rate {rate}: Load-retention correlation = {trend:.3f}"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2058: Replenishment Under Capacity Stress")
    print("=" * 60)
    print()

    exp = ReplenishmentUnderLoad()
    print(f"Parameters: D={exp.dimension}, N_crit={exp.n_crit}, φ={exp.phi:.4f}")
    print(f"Testing {exp.num_trials} trials × {exp.num_cycles} cycles each")
    print()

    results = exp.run_all_conditions()
    analysis = exp.analyze(results)

    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Hypothesis Status: {analysis['hypothesis_status']}")
    for finding in analysis["key_findings"]:
        print(f"  • {finding}")

    # Save results
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2058_replenishment_load.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
