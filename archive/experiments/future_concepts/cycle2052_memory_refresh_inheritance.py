"""
Cycle 2052: Memory Refresh to Extend Inheritance
================================================
Test if periodic memory refresh can extend the 4-generation limit.
Refresh = retrieve and re-store with clean signal.
"""

import numpy as np
import json
from datetime import datetime

class MemoryRefreshInheritance:
    def __init__(self):
        self.base_dimension = 512
        self.num_trials = 30

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

    def test_with_refresh(self, chain_depth, refresh_every):
        """Test inheritance with periodic refresh."""
        correct = 0

        for _ in range(self.num_trials):
            d = self.base_dimension

            # Create founding agent with unique memory
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)

            current_memory = self._normalize(binding)

            for i in range(chain_depth):
                # Compose with new agent
                other_key = self._generate(d)
                other_value = self._generate(d)
                other_memory = self._circ_conv(other_key, other_value)
                current_memory = self._normalize(current_memory + other_memory)

                # Periodic refresh
                if refresh_every > 0 and (i + 1) % refresh_every == 0:
                    # Retrieve and re-store with boost
                    retrieved = self._circ_corr(current_memory, key)
                    retrieved = self._normalize(retrieved)
                    # Re-add with fresh binding
                    refresh_binding = self._circ_conv(key, retrieved)
                    current_memory = self._normalize(current_memory + 0.5 * refresh_binding)

            # Test retrieval
            retrieved = self._circ_corr(current_memory, key)
            retrieved = self._normalize(retrieved)
            sim = np.dot(retrieved, value)

            if sim > 0.2:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2052: Memory Refresh to Extend Inheritance")
        print("-" * 60)

        results = []

        # Test different chain depths with/without refresh
        test_cases = [
            (5, 0, "Depth 5, no refresh"),
            (5, 2, "Depth 5, refresh/2"),
            (7, 0, "Depth 7, no refresh"),
            (7, 2, "Depth 7, refresh/2"),
            (10, 0, "Depth 10, no refresh"),
            (10, 2, "Depth 10, refresh/2"),
            (10, 3, "Depth 10, refresh/3"),
        ]

        print(f"{'Test Case':>25} | {'Survival':>10}")
        print("-" * 60)

        for depth, refresh, label in test_cases:
            acc = self.test_with_refresh(depth, refresh)
            results.append({
                "depth": depth,
                "refresh_every": refresh,
                "label": label,
                "survival_rate": acc
            })
            print(f"{label:>25} | {acc*100:>9.0f}%")

        print()
        # Analysis
        print("Refresh Effect:")
        # Compare depth 7
        no_refresh_7 = [r for r in results if r["depth"] == 7 and r["refresh_every"] == 0][0]["survival_rate"]
        with_refresh_7 = [r for r in results if r["depth"] == 7 and r["refresh_every"] == 2][0]["survival_rate"]
        gain = (with_refresh_7 - no_refresh_7) * 100
        print(f"  Depth 7: {no_refresh_7*100:.0f}% → {with_refresh_7*100:.0f}% ({gain:+.0f}%)")

        # Compare depth 10
        no_refresh_10 = [r for r in results if r["depth"] == 10 and r["refresh_every"] == 0][0]["survival_rate"]
        with_refresh_10 = [r for r in results if r["depth"] == 10 and r["refresh_every"] == 2][0]["survival_rate"]
        gain = (with_refresh_10 - no_refresh_10) * 100
        print(f"  Depth 10: {no_refresh_10*100:.0f}% → {with_refresh_10*100:.0f}% ({gain:+.0f}%)")

        return results

if __name__ == "__main__":
    exp = MemoryRefreshInheritance()
    results = exp.run()

    output = {
        "cycle": 2052,
        "experiment": "Memory Refresh Inheritance",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2052_memory_refresh_inheritance.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
