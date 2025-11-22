"""
Cycle 2039: Memory Consolidation
================================
Test if periodic reconsolidation can extend memory life.

Method: Periodically retrieve and re-store to clean up noise.
"""

import numpy as np
import json
from datetime import datetime

class MemoryConsolidation:
    def __init__(self, dimension=512):
        self.d = dimension
        self.num_trials = 50

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def consolidate(self, memory, key):
        """Retrieve and re-store to clean up noise."""
        retrieved = self._circ_corr(memory, key)
        retrieved = self._normalize(retrieved)
        new_memory = self._circ_conv(key, retrieved)
        return self._normalize(new_memory)

    def test_without_consolidation(self, num_cycles):
        """Baseline: no consolidation."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()
            memory = self._circ_conv(key, value)
            memory = self._normalize(memory)

            # Add noise each cycle
            for _ in range(num_cycles):
                noise = np.random.randn(self.d) * 0.1
                memory = self._normalize(memory + noise)

            retrieved = self._circ_corr(memory, key)
            retrieved = self._normalize(retrieved)
            if np.dot(retrieved, value) > 0.2:
                correct += 1

        return correct / self.num_trials

    def test_with_consolidation(self, num_cycles, consolidate_every):
        """With periodic consolidation."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()
            memory = self._circ_conv(key, value)
            memory = self._normalize(memory)

            for cycle in range(num_cycles):
                # Add noise
                noise = np.random.randn(self.d) * 0.1
                memory = self._normalize(memory + noise)

                # Consolidate periodically
                if (cycle + 1) % consolidate_every == 0:
                    memory = self.consolidate(memory, key)

            retrieved = self._circ_corr(memory, key)
            retrieved = self._normalize(retrieved)
            if np.dot(retrieved, value) > 0.2:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2039: Memory Consolidation")
        print("-" * 60)

        results = {}

        # Baseline
        print("Baseline (no consolidation):")
        for cycles in [1, 3, 5, 10]:
            acc = self.test_without_consolidation(cycles)
            results[f"baseline_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # With consolidation every 2 cycles
        print("\nConsolidate every 2 cycles:")
        for cycles in [3, 5, 10, 20]:
            acc = self.test_with_consolidation(cycles, 2)
            results[f"consol2_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # With consolidation every cycle
        print("\nConsolidate every cycle:")
        for cycles in [5, 10, 20, 50]:
            acc = self.test_with_consolidation(cycles, 1)
            results[f"consol1_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # Analysis
        print("\nConsolidation Effect:")
        baseline_5 = results["baseline_5"]
        consol_5 = results["consol2_5"]
        improvement = (consol_5 - baseline_5) * 100
        print(f"  5 cycles: {baseline_5*100:.0f}% → {consol_5*100:.0f}% ({improvement:+.0f}%)")

        return results

if __name__ == "__main__":
    exp = MemoryConsolidation()
    results = exp.run()

    output = {
        "cycle": 2039,
        "experiment": "Memory Consolidation",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2039_memory_consolidation.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
