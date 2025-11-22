"""
Cycle 2099: Composition with Partitioned Memories
=================================================
NRM goal is composition-decomposition dynamics.

Test: Can partitioned memories support composition operations?
- Store items across K memories
- Compose new items from existing (value combinations)
- Retrieve composed items

This validates the architecture for NRM applications.
"""

import numpy as np
import json
from datetime import datetime

class CompositionPartitionedTest:
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

    def run_trial(self, n_base, n_composed, seed):
        """Run with base items and composed items."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Store base items
        keys = []
        values = []

        for _ in range(n_base):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        # Create composed items (combine pairs of values)
        composed_keys = []
        composed_values = []

        for i in range(n_composed):
            # New key
            key = self._generate(d)

            # Composed value: average of two base values
            idx1 = i % n_base
            idx2 = (i + 1) % n_base
            composed_value = self._normalize(values[idx1] + values[idx2])

            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, composed_value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, composed_value))

            composed_keys.append(key)
            composed_values.append(composed_value)

        # All items
        all_keys = keys + composed_keys
        all_values = values + composed_values
        codebook = all_values.copy()
        all_items = list(zip(all_keys, all_values, [self._hash_key(k, self.k_memories) for k in all_keys]))

        # Run maintenance cycles
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

        # Test base items
        base_correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                base_correct += 1

        # Test composed items
        composed_correct = 0
        for key, value in zip(composed_keys, composed_values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                composed_correct += 1

        base_acc = base_correct / n_base
        composed_acc = composed_correct / n_composed if n_composed > 0 else 0

        return base_acc, composed_acc

    def run_experiment(self):
        """Test composition at various capacities."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Base':<8} {'Composed':<10} {'Total':<8} {'Base Acc':<10} {'Comp Acc':<10}")
        print("-" * 50)

        test_cases = [
            (30, 10),   # 40 total
            (40, 20),   # 60 total
            (50, 25),   # 75 total
            (60, 30),   # 90 total
        ]

        for n_base, n_composed in test_cases:
            base_accs = []
            composed_accs = []

            for trial in range(self.num_trials):
                base, comp = self.run_trial(n_base, n_composed, seed=trial*100+n_base)
                base_accs.append(base)
                composed_accs.append(comp)

            mean_base = np.mean(base_accs)
            mean_comp = np.mean(composed_accs)

            results["tests"].append({
                "n_base": n_base,
                "n_composed": n_composed,
                "n_total": n_base + n_composed,
                "base_accuracy": float(mean_base),
                "composed_accuracy": float(mean_comp)
            })

            print(f"{n_base:<8} {n_composed:<10} {n_base+n_composed:<8} {mean_base*100:>5.0f}%{'':<4} {mean_comp*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate composition performance."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check if composed items work
        for t in tests:
            if t["composed_accuracy"] >= 0.8:
                analysis["findings"].append(
                    f"{t['n_composed']} composed items at {t['composed_accuracy']*100:.0f}% (total={t['n_total']})"
                )

        # Compare base vs composed
        avg_base = np.mean([t["base_accuracy"] for t in tests])
        avg_comp = np.mean([t["composed_accuracy"] for t in tests])

        if avg_comp >= avg_base - 0.1:
            analysis["findings"].append(
                "Composed items maintain comparable accuracy to base items"
            )
            analysis["composition_works"] = True
        else:
            analysis["findings"].append(
                f"Composed items degrade: {avg_base*100:.0f}% base vs {avg_comp*100:.0f}% composed"
            )
            analysis["composition_works"] = False

        # Capacity for composition
        best = [t for t in tests if t["composed_accuracy"] >= 0.8]
        if best:
            max_comp = max(t["n_composed"] for t in best)
            analysis["findings"].append(
                f"Composition capacity: {max_comp} composed items at 80%+"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2099: Composition with Partitioned Memories")
    print("=" * 60)
    print()

    exp = CompositionPartitionedTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2099_composition_partitioned.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
