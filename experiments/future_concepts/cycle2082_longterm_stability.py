"""
Cycle 2082: Long-term Stability
===============================
Test if accuracy holds over extended operation (1000 cycles).

Previous experiments used 200 cycles. This tests:
1. Does accuracy degrade over time?
2. Is the system stable at operational capacity?
"""

import numpy as np
import json
import psutil
from datetime import datetime

class LongtermStability:
    def __init__(self):
        self.dimension = 1024
        self.n_op = int(0.0140 * self.dimension)  # 14 items
        self.num_cycles = 1000
        self.measurement_interval = 100
        self.num_trials = 3  # Fewer trials due to longer runs
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

    def run_trial(self, seed):
        """Run extended operation."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension
        n_items = self.n_op

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
        accuracy_history = []

        # Run extended cycles
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

            # Periodic measurement
            if cycle % self.measurement_interval == 0:
                correct = 0
                for key, value in zip(keys, values):
                    key_inv = np.roll(key[::-1], 1)
                    retrieved = self._circ_conv(memory, key_inv)
                    retrieved = self._cleanup(retrieved, codebook)
                    if np.dot(retrieved, value) > 0.5:
                        correct += 1
                accuracy = correct / n_items
                accuracy_history.append({
                    "cycle": cycle,
                    "accuracy": float(accuracy)
                })

        return accuracy_history

    def run_experiment(self):
        """Test long-term stability."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_op,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "trials": []
        }

        print(f"Testing {self.num_cycles} cycles with {self.n_op} items")
        print()

        all_histories = []
        for trial in range(self.num_trials):
            history = self.run_trial(seed=trial*1000)
            results["trials"].append({"trial": trial, "history": history})
            all_histories.append(history)

        # Aggregate across trials
        cycles = [h["cycle"] for h in all_histories[0]]
        aggregated = []

        print(f"{'Cycle':<10} {'Accuracy':<12}")
        print("-" * 25)

        for i, cycle in enumerate(cycles):
            accs = [all_histories[t][i]["accuracy"] for t in range(self.num_trials)]
            mean_acc = np.mean(accs)
            aggregated.append({
                "cycle": cycle,
                "mean_accuracy": float(mean_acc),
                "std_accuracy": float(np.std(accs))
            })
            print(f"{cycle:<10} {mean_acc*100:.0f}%")

        results["aggregated"] = aggregated
        return results

    def analyze(self, results):
        """Analyze stability over time."""
        agg = results["aggregated"]
        analysis = {"findings": []}

        # Initial vs final
        initial = agg[0]["mean_accuracy"]
        final = agg[-1]["mean_accuracy"]
        degradation = initial - final

        if abs(degradation) < 0.1:
            analysis["findings"].append(
                f"Stable: {initial*100:.0f}% → {final*100:.0f}% (Δ = {-degradation*100:.0f}%)"
            )
            analysis["stable"] = True
        else:
            analysis["findings"].append(
                f"Unstable: {initial*100:.0f}% → {final*100:.0f}% (Δ = {-degradation*100:.0f}%)"
            )
            analysis["stable"] = False

        # Check if always above 80%
        min_acc = min(a["mean_accuracy"] for a in agg)
        max_acc = max(a["mean_accuracy"] for a in agg)

        if min_acc >= 0.8:
            analysis["findings"].append(
                f"Always deployable: min={min_acc*100:.0f}%, max={max_acc*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                f"Drops below threshold: min={min_acc*100:.0f}%"
            )

        # Trend
        mid_idx = len(agg) // 2
        first_half = np.mean([a["mean_accuracy"] for a in agg[:mid_idx]])
        second_half = np.mean([a["mean_accuracy"] for a in agg[mid_idx:]])

        if second_half < first_half - 0.05:
            analysis["findings"].append("Warning: accuracy trending down over time")
        else:
            analysis["findings"].append("No degradation trend detected")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2082: Long-term Stability")
    print("=" * 60)
    print()

    exp = LongtermStability()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2082_longterm_stability.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
