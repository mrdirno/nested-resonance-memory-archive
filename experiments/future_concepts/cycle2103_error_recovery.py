"""
Cycle 2103: Error Recovery Test
===============================
What happens if a memory partition is corrupted?

Test: After establishing items, corrupt one memory partition.
1. Zero out the memory
2. Add Gaussian noise
3. Can remaining items recover via Hebbian refresh?

This tests system resilience to partial failures.
"""

import numpy as np
import json
from datetime import datetime

class ErrorRecoveryTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
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

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, corruption_type, seed):
        """Run with corruption and recovery."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Store items
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

        # Initial accuracy (before corruption)
        def test_accuracy():
            correct = 0
            for key, value in zip(keys, values):
                mem_idx = self._hash_key(key, self.k_memories)
                key_inv = np.roll(key[::-1], 1)
                retrieved = self._circ_conv(memories[mem_idx], key_inv)
                retrieved = self._cleanup(retrieved, codebook)
                if np.dot(retrieved, value) > 0.5:
                    correct += 1
            return correct / n_items

        acc_before = test_accuracy()

        # Find memory with most items to corrupt
        mem_sizes = [len(items) for items in memory_items]
        corrupt_idx = np.argmax(mem_sizes)
        n_corrupted = mem_sizes[corrupt_idx]

        # Apply corruption
        if corruption_type == "zero":
            memories[corrupt_idx] = np.zeros(d)
        elif corruption_type == "noise":
            memories[corrupt_idx] = np.random.normal(0, 1, d)
            memories[corrupt_idx] = self._normalize(memories[corrupt_idx])

        # Accuracy immediately after corruption
        acc_corrupted = test_accuracy()

        # Recovery: run maintenance cycles
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                mem_items = memory_items[mem_idx]
                if not mem_items:
                    continue

                noise = np.random.normal(0, 0.01, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(mem_items)
                key, value = mem_items[item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

        # Accuracy after recovery
        acc_recovered = test_accuracy()

        return acc_before, acc_corrupted, acc_recovered, n_corrupted

    def run_experiment(self):
        """Test corruption types and recovery."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "n_items": 50,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        n_items = 50

        print(f"D={self.dimension}, K={self.k_memories}, {n_items} items")
        print()
        print(f"{'Corruption':<12} {'Before':<10} {'After':<10} {'Recovered':<10} {'Items Lost':<10}")
        print("-" * 55)

        for corruption_type in ["zero", "noise"]:
            befores = []
            afters = []
            recovereds = []
            n_corrupts = []

            for trial in range(self.num_trials):
                before, after, recovered, n_corrupt = self.run_trial(
                    n_items, corruption_type, seed=trial*100
                )
                befores.append(before)
                afters.append(after)
                recovereds.append(recovered)
                n_corrupts.append(n_corrupt)

            mean_before = np.mean(befores)
            mean_after = np.mean(afters)
            mean_recovered = np.mean(recovereds)
            mean_corrupt = np.mean(n_corrupts)

            results["tests"].append({
                "corruption_type": corruption_type,
                "accuracy_before": float(mean_before),
                "accuracy_corrupted": float(mean_after),
                "accuracy_recovered": float(mean_recovered),
                "items_corrupted": float(mean_corrupt)
            })

            print(f"{corruption_type:<12} {mean_before*100:>5.0f}%{'':<4} {mean_after*100:>5.0f}%{'':<4} {mean_recovered*100:>5.0f}%{'':<4} {mean_corrupt:.0f}")

        return results

    def analyze(self, results):
        """Evaluate recovery capability."""
        tests = results["tests"]
        analysis = {"findings": []}

        for t in tests:
            recovery_pct = t["accuracy_recovered"] - t["accuracy_corrupted"]
            if recovery_pct > 0.3:
                analysis["findings"].append(
                    f"{t['corruption_type']}: Recovery +{recovery_pct*100:.0f}% "
                    f"({t['accuracy_corrupted']*100:.0f}% → {t['accuracy_recovered']*100:.0f}%)"
                )
            elif recovery_pct > 0:
                analysis["findings"].append(
                    f"{t['corruption_type']}: Partial recovery +{recovery_pct*100:.0f}%"
                )
            else:
                analysis["findings"].append(
                    f"{t['corruption_type']}: No recovery"
                )

        # Check full recovery
        for t in tests:
            if t["accuracy_recovered"] >= t["accuracy_before"] - 0.05:
                analysis["findings"].append(
                    f"{t['corruption_type']}: Full recovery to {t['accuracy_recovered']*100:.0f}%"
                )

        # Overall verdict
        recoveries = [t["accuracy_recovered"] - t["accuracy_corrupted"] for t in tests]
        if all(r > 0.3 for r in recoveries):
            analysis["findings"].append(
                "System is RESILIENT: recovers from partition loss"
            )
            analysis["resilient"] = True
        else:
            analysis["resilient"] = False

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2103: Error Recovery Test")
    print("=" * 60)
    print()

    exp = ErrorRecoveryTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2103_error_recovery.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
