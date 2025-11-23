"""
Cycle 2078: In-Operation Cleanup
================================
C2077 showed stronger Hebbian causes catastrophic interference.
C2076 showed more cycles don't help.

New approach: Periodically clean the memory during operation,
not just at retrieval. This should reduce accumulated noise
without the interference from strong Hebbian.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class InOperationCleanup:
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

    def _clean_memory(self, memory, keys, values, codebook):
        """Re-encode memory using cleaned retrievals."""
        d = len(memory)
        cleaned = np.zeros(d)
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            cleaned_value = self._cleanup(retrieved, codebook)
            binding = self._circ_conv(key, cleaned_value)
            cleaned = self._normalize(cleaned + binding)
        return cleaned

    def run_trial(self, n_items, cleanup_interval, seed):
        """Run with periodic cleanup during operation."""
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

        # Run cycles
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Hebbian refresh
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

            # Periodic cleanup
            if cleanup_interval > 0 and cycle % cleanup_interval == 0 and cycle > 0:
                memory = self._clean_memory(memory, keys, values, codebook)

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
        """Test different cleanup intervals."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "intervals": []
        }

        n_items = 20

        print(f"Testing with {n_items} items, {self.num_cycles} cycles")
        print()
        print(f"{'Interval':<15} {'Cleanups':<12} {'Accuracy':<12}")
        print("-" * 40)

        # Test intervals: never, 100, 50, 20, 10
        for interval in [0, 100, 50, 20, 10]:
            accuracies = []
            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, interval, seed=trial*100+interval)
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            num_cleanups = 0 if interval == 0 else self.num_cycles // interval - 1

            label = "never" if interval == 0 else f"every {interval}"
            results["intervals"].append({
                "interval": interval,
                "n_items": n_items,
                "num_cleanups": num_cleanups,
                "accuracy": mean_acc
            })

            print(f"{label:<15} {num_cleanups:<12} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Find optimal cleanup interval."""
        intervals = results["intervals"]
        analysis = {"findings": []}

        baseline = [i for i in intervals if i["interval"] == 0][0]
        best = max(intervals, key=lambda i: i["accuracy"])

        improvement = best["accuracy"] - baseline["accuracy"]

        if improvement > 0.1:
            label = f"every {best['interval']}" if best['interval'] > 0 else "never"
            analysis["findings"].append(
                f"In-operation cleanup helps: {label} achieves {best['accuracy']*100:.0f}% (+{improvement*100:.0f}%)"
            )
            analysis["cleanup_helps"] = True
        else:
            analysis["findings"].append(
                f"In-operation cleanup doesn't help: best {best['accuracy']*100:.0f}%"
            )
            analysis["cleanup_helps"] = False

        if best["accuracy"] >= 0.8:
            analysis["findings"].append("80% threshold achieved")
            analysis["threshold_met"] = True
        else:
            analysis["findings"].append(
                f"80% not achieved: fundamental capacity limit at 20 items"
            )
            analysis["threshold_met"] = False

        analysis["optimal_interval"] = best["interval"]
        return analysis


def main():
    print("=" * 60)
    print("Cycle 2078: In-Operation Cleanup")
    print("=" * 60)
    print()

    exp = InOperationCleanup()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2078_in_operation_cleanup.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
