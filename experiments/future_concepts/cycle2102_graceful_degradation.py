"""
Cycle 2102: Graceful Degradation Analysis
=========================================
Previous experiments showed capacity limits.
But how does accuracy degrade - gradually or suddenly?

This is critical for deployment: need predictable failure modes.

Test: Continuous accuracy curve from 10 to 150 items.
"""

import numpy as np
import json
from datetime import datetime

class GracefulDegradationTest:
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

    def run_trial(self, n_items, seed):
        """Run with specified number of items."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

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
                mem_items = memory_items[mem_idx]
                if not mem_items:
                    continue

                noise = np.random.normal(0, 0.01, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(mem_items)
                key, value = mem_items[item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_experiment(self):
        """Generate full degradation curve."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "curve": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Items':<10} {'Accuracy':<12} {'Items/Mem':<12}")
        print("-" * 35)

        # Test points: 10 to 150 in steps
        test_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150]

        for n_items in test_points:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, seed=trial*100+n_items)
                accs.append(acc)

            mean_acc = np.mean(accs)
            items_per_mem = n_items / self.k_memories

            results["curve"].append({
                "n_items": n_items,
                "accuracy": float(mean_acc),
                "items_per_memory": float(items_per_mem)
            })

            print(f"{n_items:<10} {mean_acc*100:>5.0f}%{'':<6} {items_per_mem:.1f}")

        return results

    def analyze(self, results):
        """Characterize degradation pattern."""
        curve = results["curve"]
        analysis = {"findings": []}

        # Find 80% threshold
        for i, point in enumerate(curve):
            if point["accuracy"] < 0.8:
                prev = curve[i-1] if i > 0 else point
                analysis["findings"].append(
                    f"80% threshold: {prev['n_items']}-{point['n_items']} items"
                )
                analysis["threshold_80"] = (prev["n_items"] + point["n_items"]) / 2
                break

        # Check if degradation is gradual
        accs = [p["accuracy"] for p in curve]
        diffs = [accs[i] - accs[i+1] for i in range(len(accs)-1)]

        max_drop = max(diffs) if diffs else 0
        avg_drop = np.mean(diffs) if diffs else 0

        if max_drop < 0.15:
            analysis["findings"].append(
                f"Gradual degradation: max drop = {max_drop*100:.0f}%"
            )
            analysis["degradation_type"] = "gradual"
        else:
            # Find where big drop occurs
            for i, diff in enumerate(diffs):
                if diff > 0.1:
                    analysis["findings"].append(
                        f"Sharp drop at {curve[i+1]['n_items']} items: {diff*100:.0f}%"
                    )
                    break
            analysis["degradation_type"] = "sharp"

        # Asymptotic behavior
        final_acc = curve[-1]["accuracy"]
        analysis["findings"].append(
            f"At 150 items: {final_acc*100:.0f}% (≈{150/final_acc if final_acc > 0 else 0:.0f} items equivalent)"
        )

        # Derivative
        if len(curve) >= 3:
            # Estimate items per % accuracy lost
            delta_items = curve[-1]["n_items"] - curve[0]["n_items"]
            delta_acc = curve[0]["accuracy"] - curve[-1]["accuracy"]
            if delta_acc > 0:
                items_per_pct = delta_items / (delta_acc * 100)
                analysis["findings"].append(
                    f"Rate: {items_per_pct:.1f} items per 1% accuracy loss"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2102: Graceful Degradation Analysis")
    print("=" * 60)
    print()

    exp = GracefulDegradationTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2102_graceful_degradation.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
