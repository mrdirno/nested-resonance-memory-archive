"""
Cycle 2105: Long-Term Stability Test
====================================
Previous tests used 200 cycles.
Test stability over 2000 cycles - 10× longer.

Critical question: Does accuracy remain stable or drift over time?
"""

import numpy as np
import json
from datetime import datetime

class LongTermStabilityTest:
    def __init__(self):
        self.num_trials = 2  # Fewer trials due to longer run
        self.dimension = 1024
        self.k_memories = 8
        self.total_cycles = 2000

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

    def run_trial(self, n_items, seed):
        """Run with periodic accuracy measurement."""
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

        # Track accuracy over time
        checkpoints = []

        for cycle in range(self.total_cycles):
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

            # Checkpoint every 200 cycles
            if (cycle + 1) % 200 == 0:
                acc = test_accuracy()
                checkpoints.append({
                    "cycle": cycle + 1,
                    "accuracy": float(acc)
                })

        return checkpoints

    def run_experiment(self):
        """Test long-term stability."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "total_cycles": self.total_cycles,
                "num_trials": self.num_trials,
                "n_items": 50,
                "timestamp": datetime.now().isoformat()
            },
            "checkpoints": []
        }

        n_items = 50

        print(f"D={self.dimension}, K={self.k_memories}, {n_items} items")
        print(f"Running {self.total_cycles} cycles...")
        print()
        print(f"{'Cycles':<10} {'Accuracy':<12}")
        print("-" * 25)

        # Aggregate checkpoints across trials
        checkpoint_accs = {}

        for trial in range(self.num_trials):
            checkpoints = self.run_trial(n_items, seed=trial*100)
            for cp in checkpoints:
                cycle = cp["cycle"]
                if cycle not in checkpoint_accs:
                    checkpoint_accs[cycle] = []
                checkpoint_accs[cycle].append(cp["accuracy"])

        # Average and report
        for cycle in sorted(checkpoint_accs.keys()):
            mean_acc = np.mean(checkpoint_accs[cycle])
            results["checkpoints"].append({
                "cycle": cycle,
                "accuracy": float(mean_acc)
            })
            print(f"{cycle:<10} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate stability."""
        checkpoints = results["checkpoints"]
        analysis = {"findings": []}

        accs = [cp["accuracy"] for cp in checkpoints]

        # Check drift
        first_half = accs[:len(accs)//2]
        second_half = accs[len(accs)//2:]

        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)
        drift = avg_second - avg_first

        if abs(drift) < 0.05:
            analysis["findings"].append(
                f"Stable: no drift over {results['metadata']['total_cycles']} cycles"
            )
            analysis["stable"] = True
        elif drift > 0:
            analysis["findings"].append(
                f"Improving: +{drift*100:.0f}% over time"
            )
            analysis["stable"] = True
        else:
            analysis["findings"].append(
                f"Degrading: {drift*100:.0f}% drift"
            )
            analysis["stable"] = False

        # Check variance
        std = np.std(accs)
        analysis["findings"].append(
            f"Variance: ±{std*100:.1f}%"
        )

        # Final accuracy
        final = accs[-1]
        analysis["findings"].append(
            f"Final accuracy at {results['metadata']['total_cycles']} cycles: {final*100:.0f}%"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2105: Long-Term Stability Test")
    print("=" * 60)
    print()

    exp = LongTermStabilityTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2105_long_term.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
