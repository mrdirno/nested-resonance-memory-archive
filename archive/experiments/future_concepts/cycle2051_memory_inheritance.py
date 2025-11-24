"""
Cycle 2051: Memory Inheritance Through Composition Chains
========================================================
Track how well memories survive through deep composition chains.
Test the "generational memory" hypothesis.
"""

import numpy as np
import json
from datetime import datetime

class MemoryInheritance:
    def __init__(self):
        self.base_dimension = 512
        self.num_trials = 30
        self.chain_depths = [1, 2, 3, 5, 7, 10]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def test_inheritance(self, chain_depth):
        """Track memory through composition chain."""
        correct = 0

        for _ in range(self.num_trials):
            d = self.base_dimension

            # Create founding agent with unique memory
            key = self._generate(d)
            value = self._generate(d)
            founding_memory = self._circ_conv(key, value)
            founding_memory = self._normalize(founding_memory)

            current_memory = founding_memory.copy()

            # Compose through chain
            for _ in range(chain_depth):
                # Create new agent to compose with
                other_key = self._generate(d)
                other_value = self._generate(d)
                other_memory = self._circ_conv(other_key, other_value)

                # Compose memories
                current_memory = self._normalize(current_memory + other_memory)

            # Test retrieval of founding memory
            retrieved = self._circ_corr(current_memory, key)
            retrieved = self._normalize(retrieved)
            sim = np.dot(retrieved, value)

            if sim > 0.2:  # Lower threshold for deep chains
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2051: Memory Inheritance Through Composition Chains")
        print("-" * 60)

        results = []

        print(f"{'Chain Depth':>12} | {'Survival Rate':>15} | {'Dilution':>10}")
        print("-" * 60)

        for depth in self.chain_depths:
            acc = self.test_inheritance(depth)
            dilution = 1.0 / (depth + 1)  # Theoretical signal dilution

            results.append({
                "chain_depth": depth,
                "survival_rate": acc,
                "theoretical_dilution": dilution
            })

            print(f"{depth:>12} | {acc*100:>14.0f}% | {dilution*100:>9.1f}%")

        print()
        # Analysis
        print("Inheritance Analysis:")
        base = results[0]["survival_rate"]
        for r in results[1:]:
            if r["survival_rate"] < 0.5:
                print(f"  50% inheritance lost at depth {r['chain_depth']}")
                break
        else:
            print(f"  Memories survive even at depth {self.chain_depths[-1]}")

        # Compare to theoretical
        print("\nTheoretical vs Actual:")
        for r in results:
            diff = (r["survival_rate"] - r["theoretical_dilution"]) * 100
            print(f"  depth={r['chain_depth']}: {diff:+.1f}% vs theory")

        return results

if __name__ == "__main__":
    exp = MemoryInheritance()
    results = exp.run()

    output = {
        "cycle": 2051,
        "experiment": "Memory Inheritance",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2051_memory_inheritance.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
