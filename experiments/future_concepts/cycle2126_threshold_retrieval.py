"""
Cycle 2126: Threshold-Based Retrieval
=====================================
Can we retrieve without a codebook using thresholds?

C2125 showed codebook is mandatory. Test alternatives:
1. Raw similarity threshold
2. Relative threshold (best match confidence)
3. Energy-based detection
"""

import numpy as np
import json
from datetime import datetime

class ThresholdRetrieval:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _hash_key(self, key, k_memories):
        return int(abs(key[0]) * 1000) % k_memories

    def run_trial(self, n_items, seed):
        """Test different retrieval methods."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Store
        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test different methods
        results = {}

        # Method 1: With codebook (baseline)
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)

            # Cleanup with codebook
            best_sim = -1
            best_match = None
            for clean in codebook:
                sim = np.dot(retrieved, clean)
                if sim > best_sim:
                    best_sim = sim
                    best_match = clean

            if np.dot(best_match, value) > 0.5:
                correct += 1
        results["with_codebook"] = correct / n_items

        # Method 2: Raw threshold
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._normalize(retrieved)

            if np.dot(retrieved, value) > 0.3:  # Lower threshold
                correct += 1
        results["raw_0.3"] = correct / n_items

        # Method 3: Very low threshold
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._normalize(retrieved)

            if np.dot(retrieved, value) > 0.1:
                correct += 1
        results["raw_0.1"] = correct / n_items

        # Method 4: Relative confidence (gap between top 2)
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)

            sims = [np.dot(retrieved, v) for v in codebook]
            sorted_sims = sorted(sims, reverse=True)

            if len(sorted_sims) >= 2:
                gap = sorted_sims[0] - sorted_sims[1]
                if gap > 0.05:  # Confident match
                    best_idx = np.argmax(sims)
                    if np.dot(codebook[best_idx], value) > 0.5:
                        correct += 1
        results["confidence_gap"] = correct / n_items

        return results

    def run_experiment(self):
        """Compare retrieval methods."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        n_items = 80

        print(f"D={self.dimension}, K={self.k_memories}, N={n_items}")
        print()

        # Aggregate results
        all_results = {}

        for trial in range(self.num_trials):
            trial_results = self.run_trial(n_items, seed=trial*100)
            for method, acc in trial_results.items():
                if method not in all_results:
                    all_results[method] = []
                all_results[method].append(acc)

        print(f"{'Method':<20} {'Accuracy':<10}")
        print("-" * 35)

        methods_order = ["with_codebook", "raw_0.3", "raw_0.1", "confidence_gap"]
        for method in methods_order:
            if method in all_results:
                mean_acc = np.mean(all_results[method])
                results["measurements"].append({
                    "method": method,
                    "mean_accuracy": float(mean_acc)
                })
                print(f"{method:<20} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Analyze retrieval methods."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Baseline comparison
        baseline = next((m for m in measurements if m["method"] == "with_codebook"), None)

        for m in measurements:
            if m["method"] != "with_codebook" and baseline:
                diff = (m["mean_accuracy"] - baseline["mean_accuracy"]) * 100
                analysis["findings"].append(
                    f"{m['method']}: {diff:+.0f}% vs codebook"
                )

        # Best alternative
        alternatives = [m for m in measurements if m["method"] != "with_codebook"]
        if alternatives:
            best = max(alternatives, key=lambda x: x["mean_accuracy"])
            analysis["findings"].append(
                f"Best alternative: {best['method']} at {best['mean_accuracy']*100:.0f}%"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2126: Threshold-Based Retrieval")
    print("=" * 60)
    print()

    exp = ThresholdRetrieval()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2126_threshold_retrieval.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
