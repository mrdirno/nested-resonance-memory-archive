"""
Cycle 2038: Memory Degradation Through Cycles
=============================================
Test how memory quality degrades through repeated
composition-decomposition operations.
"""

import numpy as np
import json
from datetime import datetime

class MemoryDegradation:
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

    def test_composition_chain(self, chain_length):
        """Track memory through chain of compositions."""
        correct = 0

        for _ in range(self.num_trials):
            # Original pattern
            key = self._generate()
            value = self._generate()

            # Create initial memory
            memory = self._circ_conv(key, value)
            memory = self._normalize(memory)

            # Chain of compositions with other memories
            for _ in range(chain_length):
                other_key = self._generate()
                other_value = self._generate()
                other_memory = self._circ_conv(other_key, other_value)
                memory = self._normalize(memory + other_memory)

            # Retrieve
            retrieved = self._circ_corr(memory, key)
            retrieved = self._normalize(retrieved)
            sim = np.dot(retrieved, value)

            if sim > 0.2:
                correct += 1

        return correct / self.num_trials

    def test_decomposition_chain(self, chain_length):
        """Track memory through chain of decompositions."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()
            memory = self._circ_conv(key, value)
            memory = self._normalize(memory)

            # Chain of decompositions
            for _ in range(chain_length):
                noise = np.random.randn(self.d) * 0.1
                memory = self._normalize(memory + noise)

            retrieved = self._circ_corr(memory, key)
            retrieved = self._normalize(retrieved)
            sim = np.dot(retrieved, value)

            if sim > 0.2:
                correct += 1

        return correct / self.num_trials

    def test_mixed_chain(self, num_cycles):
        """Track through mixed composition-decomposition."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()
            memory = self._circ_conv(key, value)
            memory = self._normalize(memory)

            for _ in range(num_cycles):
                # Random composition
                if np.random.random() < 0.5:
                    other = self._circ_conv(self._generate(), self._generate())
                    memory = self._normalize(memory + other)
                # Random decomposition noise
                else:
                    noise = np.random.randn(self.d) * 0.1
                    memory = self._normalize(memory + noise)

            retrieved = self._circ_corr(memory, key)
            retrieved = self._normalize(retrieved)
            sim = np.dot(retrieved, value)

            if sim > 0.2:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2038: Memory Degradation Through Cycles")
        print("-" * 60)

        results = {"composition": {}, "decomposition": {}, "mixed": {}}

        # Composition chains
        print("\nComposition Chain Length:")
        for length in [1, 2, 3, 5, 10]:
            acc = self.test_composition_chain(length)
            results["composition"][str(length)] = acc
            print(f"  {length} compositions: {acc*100:.0f}%")

        # Decomposition chains
        print("\nDecomposition Chain Length:")
        for length in [1, 2, 3, 5, 10]:
            acc = self.test_decomposition_chain(length)
            results["decomposition"][str(length)] = acc
            print(f"  {length} decompositions: {acc*100:.0f}%")

        # Mixed chains
        print("\nMixed Cycles:")
        for cycles in [1, 5, 10, 20]:
            acc = self.test_mixed_chain(cycles)
            results["mixed"][str(cycles)] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # Analysis
        print("\nDegradation Analysis:")
        comp_degradation = results["composition"]["1"] - results["composition"]["10"]
        print(f"  Composition (1→10): {comp_degradation*100:+.0f}%")
        decomp_degradation = results["decomposition"]["1"] - results["decomposition"]["10"]
        print(f"  Decomposition (1→10): {decomp_degradation*100:+.0f}%")
        mixed_degradation = results["mixed"]["1"] - results["mixed"]["20"]
        print(f"  Mixed (1→20): {mixed_degradation*100:+.0f}%")

        return results

if __name__ == "__main__":
    exp = MemoryDegradation()
    results = exp.run()

    output = {
        "cycle": 2038,
        "experiment": "Memory Degradation",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2038_memory_degradation.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
