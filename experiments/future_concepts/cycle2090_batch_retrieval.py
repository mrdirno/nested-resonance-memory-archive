"""
Cycle 2090: Batch Retrieval Performance
=======================================
Test simultaneous retrieval of multiple items.

This simulates real deployment where multiple queries
may need to be processed together.
"""

import numpy as np
import json
import psutil
import time
from datetime import datetime

class BatchRetrieval:
    def __init__(self):
        self.dimension = 1024
        self.n_items = 10
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

    def run_trial(self, batch_size, seed):
        """Test batch retrieval of given size."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Run operation
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % self.n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Batch retrieval - select batch_size random queries
        query_indices = np.random.choice(self.n_items, batch_size, replace=False)

        start_time = time.time()

        # Retrieve all in batch
        batch_correct = 0
        for idx in query_indices:
            key_inv = np.roll(keys[idx][::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, values[idx]) > 0.5:
                batch_correct += 1

        elapsed = time.time() - start_time

        return {
            "batch_size": batch_size,
            "accuracy": batch_correct / batch_size,
            "time_ms": elapsed * 1000,
            "time_per_item_ms": elapsed * 1000 / batch_size
        }

    def run_experiment(self):
        """Test different batch sizes."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "batches": []
        }

        print(f"Testing batch retrieval performance")
        print()
        print(f"{'Batch':<10} {'Accuracy':<12} {'Time/Item (ms)':<15}")
        print("-" * 40)

        for batch_size in [1, 2, 5, 10]:
            accs = []
            times = []

            for trial in range(self.num_trials):
                result = self.run_trial(batch_size, seed=trial*100+batch_size)
                accs.append(result["accuracy"])
                times.append(result["time_per_item_ms"])

            mean_acc = float(np.mean(accs))
            mean_time = float(np.mean(times))

            results["batches"].append({
                "batch_size": batch_size,
                "accuracy": mean_acc,
                "time_per_item_ms": mean_time
            })

            print(f"{batch_size:<10} {mean_acc*100:.0f}%{'':<10} {mean_time:.2f}")

        return results

    def analyze(self, results):
        """Analyze batch performance."""
        batches = results["batches"]
        analysis = {"findings": []}

        # Check if accuracy constant across batch sizes
        accs = [b["accuracy"] for b in batches]
        if max(accs) - min(accs) < 0.1:
            analysis["findings"].append(
                f"Accuracy stable across batch sizes: {min(accs)*100:.0f}%-{max(accs)*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                f"Accuracy varies with batch: {min(accs)*100:.0f}%-{max(accs)*100:.0f}%"
            )

        # Check scaling
        single = [b for b in batches if b["batch_size"] == 1][0]
        full = [b for b in batches if b["batch_size"] == 10][0]

        speedup = single["time_per_item_ms"] / full["time_per_item_ms"]
        analysis["findings"].append(
            f"Batch efficiency: {speedup:.1f}× vs single retrieval"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2090: Batch Retrieval Performance")
    print("=" * 60)
    print()

    exp = BatchRetrieval()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2090_batch_retrieval.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
