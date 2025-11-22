"""
Cycle 2123: Warmup Duration vs Load
===================================
Does optimal warmup change with item count?

C2122 found 10 cycles sufficient at 80 items.
Test across different loads.
"""

import numpy as np
import json
from datetime import datetime

class WarmupVsLoad:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3

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

    def find_warmup(self, n_items, seed, target_acc=0.95):
        """Find cycles needed to reach target accuracy."""
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

        # Find warmup duration
        for cycle in range(501):
            # Check accuracy
            correct = 0
            for key, value in zip(keys, values):
                mem_idx = self._hash_key(key, self.k_memories)
                key_inv = np.roll(key[::-1], 1)
                retrieved = self._circ_conv(memories[mem_idx], key_inv)
                retrieved = self._cleanup(retrieved, codebook)
                if np.dot(retrieved, value) > 0.5:
                    correct += 1

            acc = correct / n_items
            if acc >= target_acc:
                return cycle, acc

            # Maintenance
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        return 500, acc  # Didn't reach target

    def run_experiment(self):
        """Test warmup across loads."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Items':<8} {'Load %':<10} {'Warmup':<10} {'Final Acc':<12}")
        print("-" * 45)

        # K × 12 = 96 items at capacity
        for n_items in [24, 48, 72, 96, 120]:
            load_pct = (n_items / 96) * 100

            warmups = []
            final_accs = []

            for trial in range(self.num_trials):
                cycles, acc = self.find_warmup(n_items, seed=trial*100+n_items)
                warmups.append(cycles)
                final_accs.append(acc)

            mean_warmup = np.mean(warmups)
            mean_acc = np.mean(final_accs)

            results["measurements"].append({
                "n_items": n_items,
                "load_percent": float(load_pct),
                "mean_warmup": float(mean_warmup),
                "warmup_std": float(np.std(warmups)),
                "mean_accuracy": float(mean_acc)
            })

            print(f"{n_items:<8} {load_pct:>5.0f}%{'':<3} {mean_warmup:>5.0f}{'':<4} {mean_acc*100:>5.1f}%")

        return results

    def analyze(self, results):
        """Analyze warmup scaling."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Find pattern
        loads = [m["load_percent"] for m in measurements]
        warmups = [m["mean_warmup"] for m in measurements]

        # Linear fit
        slope, intercept = np.polyfit(loads, warmups, 1)
        analysis["findings"].append(
            f"Warmup formula: {intercept:.0f} + {slope:.2f} × load%"
        )

        # Check if constant
        if np.std(warmups) < 5:
            analysis["findings"].append(
                f"Warmup nearly constant: {np.mean(warmups):.0f} cycles"
            )
        else:
            analysis["findings"].append(
                f"Warmup scales with load: {min(warmups):.0f} to {max(warmups):.0f} cycles"
            )

        # At 100% load
        at_100 = next((m for m in measurements if m["load_percent"] >= 100), None)
        if at_100:
            analysis["findings"].append(
                f"At full load: {at_100['mean_warmup']:.0f} cycles for {at_100['mean_accuracy']*100:.0f}%"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2123: Warmup Duration vs Load")
    print("=" * 60)
    print()

    exp = WarmupVsLoad()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2123_warmup_vs_load.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
