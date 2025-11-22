"""
Cycle 2107: Hebbian Strength Sensitivity
========================================
Current implementation uses 0.5× Hebbian strength.

Test: What's the optimal strength?
- Too weak: signals fade
- Too strong: interference (C2077 showed this)

Find the sweet spot.
"""

import numpy as np
import json
from datetime import datetime

class HebbianStrengthTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
        self.num_cycles = 200
        self.n_items = 50

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

    def run_trial(self, strength, seed):
        """Run with specified Hebbian strength."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        for _ in range(self.n_items):
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
                memories[mem_idx] = self._normalize(memories[mem_idx] + strength * binding)

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / self.n_items

    def run_experiment(self):
        """Test various Hebbian strengths."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "n_items": self.n_items,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "strengths": []
        }

        print(f"D={self.dimension}, K={self.k_memories}, {self.n_items} items")
        print()
        print(f"{'Strength':<12} {'Accuracy':<12}")
        print("-" * 25)

        strengths = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5]

        for strength in strengths:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(strength, seed=trial*100+int(strength*100))
                accs.append(acc)

            mean_acc = np.mean(accs)

            results["strengths"].append({
                "strength": strength,
                "accuracy": float(mean_acc)
            })

            print(f"{strength:<12} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Find optimal strength."""
        strengths = results["strengths"]
        analysis = {"findings": []}

        # Find optimal
        best = max(strengths, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Optimal strength: {best['strength']}× ({best['accuracy']*100:.0f}%)"
        )
        analysis["optimal_strength"] = best["strength"]

        # Compare to 0.5
        s05 = [s for s in strengths if s["strength"] == 0.5][0]
        diff = best["accuracy"] - s05["accuracy"]
        if abs(diff) < 0.05:
            analysis["findings"].append(
                f"Current 0.5× is near-optimal (within {abs(diff)*100:.0f}%)"
            )
        elif diff > 0:
            analysis["findings"].append(
                f"Can improve by using {best['strength']}× (+{diff*100:.0f}%)"
            )

        # Safe range
        safe = [s for s in strengths if s["accuracy"] >= 0.9]
        if safe:
            strengths_range = [s["strength"] for s in safe]
            analysis["findings"].append(
                f"Safe range: {min(strengths_range)}× to {max(strengths_range)}×"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2107: Hebbian Strength Sensitivity")
    print("=" * 60)
    print()

    exp = HebbianStrengthTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2107_hebbian_strength.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
