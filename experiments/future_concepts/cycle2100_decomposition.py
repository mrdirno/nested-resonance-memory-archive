"""
Cycle 2100: Decomposition Test
==============================
C2099 validated composition. Now test decomposition.

Can we retrieve components from composed items?
If composed_value = normalize(v1 + v2), can retrieval get v1 and v2?

Test: Store base items and their compositions.
Then test if composed values can be decomposed back to components.
"""

import numpy as np
import json
from datetime import datetime

class DecompositionTest:
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
        """Test decomposition of composed items."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Store base items
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

        # Create composed items with tracked components
        composed_keys = []
        composed_values = []
        component_pairs = []  # (idx1, idx2) for each composed

        for i in range(n_composed):
            key = self._generate(d)

            # Compose from two base values
            idx1 = i % n_base
            idx2 = (i + 3) % n_base  # Different offset
            composed_value = self._normalize(base_values[idx1] + base_values[idx2])

            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, composed_value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, composed_value))

            composed_keys.append(key)
            composed_values.append(composed_value)
            component_pairs.append((idx1, idx2))

        # All items for refresh
        all_items = list(zip(base_keys + composed_keys,
                            base_values + composed_values,
                            [self._hash_key(k, self.k_memories) for k in base_keys + composed_keys]))

        # Codebook is base values only (for decomposition)
        base_codebook = base_values.copy()

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

        # Test base retrieval
        base_correct = 0
        for key, value in zip(base_keys, base_values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, base_codebook)
            if np.dot(retrieved, value) > 0.5:
                base_correct += 1

        # Test decomposition: can composed values be matched to components?
        decomp_correct = 0
        for i, (key, composed_value) in enumerate(zip(composed_keys, composed_values)):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)

            # Check similarity to both components
            idx1, idx2 = component_pairs[i]
            comp1 = base_values[idx1]
            comp2 = base_values[idx2]

            sim1 = np.dot(retrieved, comp1)
            sim2 = np.dot(retrieved, comp2)

            # Decomposition success: retrieved vector is similar to both components
            if sim1 > 0.3 and sim2 > 0.3:
                decomp_correct += 1

        base_acc = base_correct / n_base
        decomp_acc = decomp_correct / n_composed if n_composed > 0 else 0

        return base_acc, decomp_acc

    def run_experiment(self):
        """Test decomposition at various scales."""
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
        print(f"{'Base':<8} {'Composed':<10} {'Total':<8} {'Base Acc':<10} {'Decomp':<10}")
        print("-" * 50)

        test_cases = [
            (20, 10),   # 30 total
            (30, 15),   # 45 total
            (40, 20),   # 60 total
            (50, 25),   # 75 total
        ]

        for n_base, n_composed in test_cases:
            base_accs = []
            decomp_accs = []

            for trial in range(self.num_trials):
                base, decomp = self.run_trial(n_base, n_composed, seed=trial*100+n_base)
                base_accs.append(base)
                decomp_accs.append(decomp)

            mean_base = np.mean(base_accs)
            mean_decomp = np.mean(decomp_accs)

            results["tests"].append({
                "n_base": n_base,
                "n_composed": n_composed,
                "n_total": n_base + n_composed,
                "base_accuracy": float(mean_base),
                "decomposition_accuracy": float(mean_decomp)
            })

            print(f"{n_base:<8} {n_composed:<10} {n_base+n_composed:<8} {mean_base*100:>5.0f}%{'':<4} {mean_decomp*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate decomposition performance."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check decomposition success
        avg_decomp = np.mean([t["decomposition_accuracy"] for t in tests])

        if avg_decomp >= 0.8:
            analysis["findings"].append(
                f"Decomposition works: {avg_decomp*100:.0f}% avg accuracy"
            )
            analysis["decomposition_works"] = True
        elif avg_decomp >= 0.5:
            analysis["findings"].append(
                f"Partial decomposition: {avg_decomp*100:.0f}% avg (threshold 0.3)"
            )
            analysis["decomposition_works"] = True
        else:
            analysis["findings"].append(
                f"Decomposition fails: {avg_decomp*100:.0f}% avg"
            )
            analysis["decomposition_works"] = False

        # Best case
        best = max(tests, key=lambda t: t["decomposition_accuracy"])
        analysis["findings"].append(
            f"Best: {best['n_composed']} composed at {best['decomposition_accuracy']*100:.0f}%"
        )

        # Compare to base
        avg_base = np.mean([t["base_accuracy"] for t in tests])
        if avg_decomp >= avg_base - 0.2:
            analysis["findings"].append(
                "Decomposition comparable to base retrieval"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2100: Decomposition Test")
    print("=" * 60)
    print()

    exp = DecompositionTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2100_decomposition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
