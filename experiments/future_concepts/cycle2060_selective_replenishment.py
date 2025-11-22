"""
Cycle 2060: Selective Replenishment Strategy
=============================================
Test if intelligent targeting can beat uniform replenishment.

From C2058-C2059:
- R_crit ≈ 0.22 is the survival floor (constant)
- Above R_crit, retention quality degrades with load

Hypothesis: Selective replenishment (target weakest memories) achieves
higher retention than random replenishment at the same rate.
"""

import numpy as np
import json
from datetime import datetime

class SelectiveReplenishment:
    def __init__(self):
        self.dimension = 1024
        self.n_crit = int(0.042 * self.dimension)
        self.phi = (1 + np.sqrt(5)) / 2
        self.num_cycles = 300
        self.num_trials = 10
        self.replenish_rate = 0.25  # Above R_crit

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

    def _get_item_strength(self, memory, key, value):
        """Get retrieval strength for a single item."""
        key_inv = np.roll(key[::-1], 1)
        retrieved = self._normalize(self._circ_conv(memory, key_inv))
        return np.dot(retrieved, value)

    def _recall_accuracy(self, memory, keys, values):
        correct = 0
        for key, value in zip(keys, values):
            strength = self._get_item_strength(memory, key, value)
            if strength > 0.1:
                correct += 1
        return correct / len(keys) if keys else 0

    def run_trial(self, load_fraction, strategy, seed):
        """Run single trial with given strategy."""
        np.random.seed(seed)

        n_items = max(1, int(load_fraction * self.n_crit))
        d = self.dimension

        memory, keys, values = self._store_items(n_items)
        initial_accuracy = self._recall_accuracy(memory, keys, values)

        if initial_accuracy == 0:
            return {"retention": 0, "final_accuracy": 0}

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

            # Replenishment with strategy
            if np.random.random() < self.replenish_rate:
                if strategy == "random":
                    idx = np.random.randint(len(keys))
                elif strategy == "weakest":
                    # Find weakest memory
                    strengths = [self._get_item_strength(memory, k, v)
                                for k, v in zip(keys, values)]
                    idx = np.argmin(strengths)
                elif strategy == "strongest":
                    # Baseline: reinforce already strong memories
                    strengths = [self._get_item_strength(memory, k, v)
                                for k, v in zip(keys, values)]
                    idx = np.argmax(strengths)
                elif strategy == "round_robin":
                    # Systematic cycling through all items
                    idx = cycle % len(keys)
                else:
                    idx = np.random.randint(len(keys))

                binding = self._circ_conv(keys[idx], values[idx])
                memory = self._normalize(memory + 0.5 * binding)

        final_accuracy = self._recall_accuracy(memory, keys, values)
        retention = final_accuracy / initial_accuracy if initial_accuracy > 0 else 0

        return {
            "initial_accuracy": initial_accuracy,
            "final_accuracy": final_accuracy,
            "retention": retention
        }

    def run_experiment(self):
        """Compare strategies across load levels."""
        load_fractions = [0.5, 0.75, 1.0]
        strategies = ["random", "weakest", "strongest", "round_robin"]

        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_crit": self.n_crit,
                "replenish_rate": self.replenish_rate,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Load':<8} {'Strategy':<12} {'Retention':<12} {'Final Acc':<12}")
        print("-" * 50)

        for load in load_fractions:
            for strategy in strategies:
                trial_results = []
                for trial in range(self.num_trials):
                    result = self.run_trial(load, strategy, seed=trial*100)
                    trial_results.append(result)

                mean_retention = np.mean([r["retention"] for r in trial_results])
                mean_final = np.mean([r["final_accuracy"] for r in trial_results])
                std_retention = np.std([r["retention"] for r in trial_results])

                condition = {
                    "load_fraction": load,
                    "strategy": strategy,
                    "mean_retention": float(mean_retention),
                    "std_retention": float(std_retention),
                    "mean_final_accuracy": float(mean_final)
                }
                results["conditions"].append(condition)

                print(f"{load*100:<8.0f}% {strategy:<12} {mean_retention:<12.3f} {mean_final:<12.3f}")

        return results

    def analyze(self, results):
        """Determine best strategy."""
        conditions = results["conditions"]

        analysis = {
            "strategy_ranking": [],
            "hypothesis_status": "UNKNOWN"
        }

        # Compare at 100% load
        load_100 = [c for c in conditions if c["load_fraction"] == 1.0]
        sorted_strats = sorted(load_100, key=lambda x: x["mean_retention"], reverse=True)

        for i, s in enumerate(sorted_strats):
            analysis["strategy_ranking"].append({
                "rank": i + 1,
                "strategy": s["strategy"],
                "retention": s["mean_retention"]
            })

        # Test hypothesis
        weakest = [c for c in load_100 if c["strategy"] == "weakest"][0]
        random = [c for c in load_100 if c["strategy"] == "random"][0]

        improvement = weakest["mean_retention"] - random["mean_retention"]

        if improvement > 0.05:
            analysis["hypothesis_status"] = "CONFIRMED"
            analysis["improvement"] = f"Selective targeting improves retention by {improvement*100:.1f}%"
        elif improvement > 0:
            analysis["hypothesis_status"] = "PARTIAL"
            analysis["improvement"] = f"Marginal improvement: {improvement*100:.1f}%"
        else:
            analysis["hypothesis_status"] = "FALSIFIED"
            analysis["improvement"] = f"No improvement (diff={improvement*100:.1f}%)"

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2060: Selective Replenishment Strategy")
    print("=" * 60)
    print()

    exp = SelectiveReplenishment()
    print(f"D={exp.dimension}, N_crit={exp.n_crit}, Rate={exp.replenish_rate}")
    print()

    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Hypothesis: {analysis['hypothesis_status']}")
    print(f"Finding: {analysis.get('improvement', 'N/A')}")
    print()
    print("Strategy Ranking at 100% Load:")
    for s in analysis["strategy_ranking"]:
        print(f"  {s['rank']}. {s['strategy']}: {s['retention']:.3f}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2060_selective_replenishment.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
