"""
Cycle 2095: Multiple Memories (Partitioning)
============================================
C2094 showed orthogonal keys don't help - plateau is fundamental.

Hypothesis: Multiple memory vectors can scale capacity.
If single memory holds ~16 items, K memories should hold ~16K items.

Test: Partition items across K memory vectors using key hash.
"""

import numpy as np
import json
from datetime import datetime

class MultipleMemoriesTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
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
        """Simple hash: use first component to select memory."""
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

    def run_single_memory(self, n_items, seed):
        """Baseline: single memory."""
        np.random.seed(seed)
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

        codebook = values.copy()

        # Operation cycles
        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)
            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_multiple_memories(self, n_items, k_memories, seed):
        """Partitioned: k separate memories."""
        np.random.seed(seed)
        d = self.dimension

        # Initialize k memories
        memories = [np.zeros(d) for _ in range(k_memories)]
        memory_items = [[] for _ in range(k_memories)]  # Track items per memory

        keys = []
        values = []

        # Store items with hashing
        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)

            # Hash to select memory
            mem_idx = self._hash_key(key, k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Operation cycles (cycle through all memories)
        for cycle in range(self.num_cycles):
            for mem_idx in range(k_memories):
                if len(memory_items[mem_idx]) > 0:
                    noise = np.random.normal(0, 0.01, d)
                    memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                    items = memory_items[mem_idx]
                    item_idx = cycle % len(items)
                    key, value = items[item_idx]
                    binding = self._circ_conv(key, value)
                    memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_experiment(self):
        """Compare single vs multiple memories."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "comparisons": []
        }

        print(f"D = {self.dimension}, comparing single vs partitioned memory...")
        print()
        print(f"{'Items':<8} {'Single':<10} {'K=2':<10} {'K=4':<10} {'K=8':<10}")
        print("-" * 50)

        for n_items in [16, 32, 48, 64]:
            single_accs = []
            k2_accs = []
            k4_accs = []
            k8_accs = []

            for trial in range(self.num_trials):
                single_accs.append(self.run_single_memory(n_items, seed=trial*100+n_items))
                k2_accs.append(self.run_multiple_memories(n_items, 2, seed=trial*100+n_items))
                k4_accs.append(self.run_multiple_memories(n_items, 4, seed=trial*100+n_items))
                k8_accs.append(self.run_multiple_memories(n_items, 8, seed=trial*100+n_items))

            results["comparisons"].append({
                "n_items": n_items,
                "single": float(np.mean(single_accs)),
                "k2": float(np.mean(k2_accs)),
                "k4": float(np.mean(k4_accs)),
                "k8": float(np.mean(k8_accs))
            })

            print(f"{n_items:<8} {np.mean(single_accs)*100:>5.0f}%{'':<4} {np.mean(k2_accs)*100:>5.0f}%{'':<4} {np.mean(k4_accs)*100:>5.0f}%{'':<4} {np.mean(k8_accs)*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate multiple memory benefit."""
        comps = results["comparisons"]
        analysis = {"findings": []}

        # Check scaling
        for c in comps:
            if c["k8"] >= 0.8 and c["single"] < 0.5:
                analysis["findings"].append(
                    f"{c['n_items']} items: single={c['single']*100:.0f}%, K=8={c['k8']*100:.0f}%"
                )

        # Check if we can reach 64 items
        c64 = [c for c in comps if c["n_items"] == 64][0]
        if c64["k8"] >= 0.8:
            analysis["findings"].append(
                "SUCCESS: K=8 memories achieves 80%+ at 64 items!"
            )
            analysis["scales"] = True
        else:
            best = max(c64["k2"], c64["k4"], c64["k8"])
            analysis["findings"].append(
                f"64 items best: {best*100:.0f}% (needs more memories)"
            )
            analysis["scales"] = c64["k8"] > c64["single"] + 0.2

        # Scaling factor
        if comps[-1]["k8"] > 0 and comps[-1]["single"] > 0:
            factor = comps[-1]["k8"] / comps[-1]["single"]
            analysis["findings"].append(
                f"K=8 provides {factor:.1f}× accuracy improvement at high capacity"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2095: Multiple Memories (Partitioning)")
    print("=" * 60)
    print()

    exp = MultipleMemoriesTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2095_multiple_memories.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
