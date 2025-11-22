"""
Cycle 2101: Hierarchical Composition Test
=========================================
C2099 showed composition works, C2100 showed decomposition fails.

Test: Can we compose from already-composed items?
Level 0: Base values
Level 1: Composed from pairs of base
Level 2: Composed from pairs of Level 1

This tests deeper NRM hierarchical structures.
"""

import numpy as np
import json
from datetime import datetime

class HierarchicalCompositionTest:
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

    def run_trial(self, n_base, seed):
        """Run hierarchical composition trial."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Level 0: Base items
        base_keys = []
        base_values = []

        for _ in range(n_base):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            base_keys.append(key)
            base_values.append(value)

        # Level 1: Compose pairs of base
        level1_keys = []
        level1_values = []
        n_level1 = n_base // 2

        for i in range(n_level1):
            key = self._generate(d)
            composed = self._normalize(base_values[2*i] + base_values[2*i + 1])
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, composed)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, composed))

            level1_keys.append(key)
            level1_values.append(composed)

        # Level 2: Compose pairs of Level 1
        level2_keys = []
        level2_values = []
        n_level2 = n_level1 // 2

        for i in range(n_level2):
            key = self._generate(d)
            composed = self._normalize(level1_values[2*i] + level1_values[2*i + 1])
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, composed)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, composed))

            level2_keys.append(key)
            level2_values.append(composed)

        # All items
        all_values = base_values + level1_values + level2_values
        codebook = all_values.copy()

        # Run maintenance
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

        # Test each level
        def test_level(keys, values, name):
            correct = 0
            for key, value in zip(keys, values):
                mem_idx = self._hash_key(key, self.k_memories)
                key_inv = np.roll(key[::-1], 1)
                retrieved = self._circ_conv(memories[mem_idx], key_inv)
                retrieved = self._cleanup(retrieved, codebook)
                if np.dot(retrieved, value) > 0.5:
                    correct += 1
            return correct / len(values) if values else 0

        base_acc = test_level(base_keys, base_values, "base")
        level1_acc = test_level(level1_keys, level1_values, "level1")
        level2_acc = test_level(level2_keys, level2_values, "level2")

        return base_acc, level1_acc, level2_acc, len(base_values), len(level1_values), len(level2_values)

    def run_experiment(self):
        """Test hierarchical composition at various scales."""
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
        print(f"{'Base':<8} {'L1':<8} {'L2':<8} {'Total':<8} {'Base%':<8} {'L1%':<8} {'L2%':<8}")
        print("-" * 60)

        for n_base in [16, 24, 32, 40]:
            base_accs = []
            l1_accs = []
            l2_accs = []

            for trial in range(self.num_trials):
                base, l1, l2, nb, nl1, nl2 = self.run_trial(n_base, seed=trial*100+n_base)
                base_accs.append(base)
                l1_accs.append(l1)
                l2_accs.append(l2)

            mean_base = np.mean(base_accs)
            mean_l1 = np.mean(l1_accs)
            mean_l2 = np.mean(l2_accs)
            n_l1 = n_base // 2
            n_l2 = n_l1 // 2
            total = n_base + n_l1 + n_l2

            results["tests"].append({
                "n_base": n_base,
                "n_level1": n_l1,
                "n_level2": n_l2,
                "n_total": total,
                "base_accuracy": float(mean_base),
                "level1_accuracy": float(mean_l1),
                "level2_accuracy": float(mean_l2)
            })

            print(f"{n_base:<8} {n_l1:<8} {n_l2:<8} {total:<8} {mean_base*100:>5.0f}%{'':<2} {mean_l1*100:>5.0f}%{'':<2} {mean_l2*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate hierarchical composition."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check Level 2 success
        avg_l2 = np.mean([t["level2_accuracy"] for t in tests])

        if avg_l2 >= 0.8:
            analysis["findings"].append(
                f"Hierarchical composition works: L2 = {avg_l2*100:.0f}%"
            )
            analysis["hierarchical_works"] = True
        else:
            analysis["findings"].append(
                f"L2 accuracy lower: {avg_l2*100:.0f}% (vs 80% threshold)"
            )
            analysis["hierarchical_works"] = avg_l2 >= 0.6

        # Compare levels
        avg_base = np.mean([t["base_accuracy"] for t in tests])
        avg_l1 = np.mean([t["level1_accuracy"] for t in tests])

        analysis["findings"].append(
            f"Level progression: Base {avg_base*100:.0f}% → L1 {avg_l1*100:.0f}% → L2 {avg_l2*100:.0f}%"
        )

        # Degradation per level
        if avg_l1 > 0 and avg_l2 > 0:
            deg_l1 = (avg_base - avg_l1) / avg_base * 100
            deg_l2 = (avg_l1 - avg_l2) / avg_l1 * 100
            if deg_l1 > 5 or deg_l2 > 5:
                analysis["findings"].append(
                    f"Degradation per level: {deg_l1:.0f}% (L1), {deg_l2:.0f}% (L2)"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2101: Hierarchical Composition Test")
    print("=" * 60)
    print()

    exp = HierarchicalCompositionTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2101_hierarchical_composition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
