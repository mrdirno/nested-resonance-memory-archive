"""
Cycle 2040: Voting-Based Consolidation
======================================
Use multiple independent noisy copies + averaging for consolidation.
Combines C2033 (voting correction) with C2039 (consolidation).
"""

import numpy as np
import json
from datetime import datetime

class VotingConsolidation:
    def __init__(self, dimension=512):
        self.d = dimension
        self.num_trials = 50
        self.num_copies = 3  # Based on C2033 finding

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

    def voting_consolidate(self, memories, key):
        """Consolidate by averaging retrievals from multiple copies."""
        retrieved_sum = np.zeros(self.d)
        for memory in memories:
            r = self._circ_corr(memory, key)
            retrieved_sum += r
        retrieved = self._normalize(retrieved_sum)
        new_memory = self._circ_conv(key, retrieved)
        return self._normalize(new_memory)

    def test_voting_consolidation(self, num_cycles, consolidate_every):
        """Test with voting-based consolidation."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()

            # Create multiple independent copies
            memories = []
            for _ in range(self.num_copies):
                mem = self._circ_conv(key, value)
                memories.append(self._normalize(mem))

            for cycle in range(num_cycles):
                # Add independent noise to each copy
                for i in range(len(memories)):
                    noise = np.random.randn(self.d) * 0.1
                    memories[i] = self._normalize(memories[i] + noise)

                # Voting consolidation periodically
                if (cycle + 1) % consolidate_every == 0:
                    consolidated = self.voting_consolidate(memories, key)
                    memories = [consolidated.copy() for _ in range(self.num_copies)]

            # Test retrieval from averaged copies
            retrieved_sum = np.zeros(self.d)
            for mem in memories:
                r = self._circ_corr(mem, key)
                retrieved_sum += r
            retrieved = self._normalize(retrieved_sum)

            if np.dot(retrieved, value) > 0.2:
                correct += 1

        return correct / self.num_trials

    def test_baseline(self, num_cycles):
        """Baseline with voting but no consolidation."""
        correct = 0

        for _ in range(self.num_trials):
            key = self._generate()
            value = self._generate()

            memories = []
            for _ in range(self.num_copies):
                mem = self._circ_conv(key, value)
                memories.append(self._normalize(mem))

            for _ in range(num_cycles):
                for i in range(len(memories)):
                    noise = np.random.randn(self.d) * 0.1
                    memories[i] = self._normalize(memories[i] + noise)

            retrieved_sum = np.zeros(self.d)
            for mem in memories:
                r = self._circ_corr(mem, key)
                retrieved_sum += r
            retrieved = self._normalize(retrieved_sum)

            if np.dot(retrieved, value) > 0.2:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2040: Voting-Based Consolidation")
        print("-" * 60)

        results = {}

        # Baseline (voting only)
        print(f"Baseline (voting, no consolidation, {self.num_copies} copies):")
        for cycles in [1, 3, 5, 10, 20]:
            acc = self.test_baseline(cycles)
            results[f"baseline_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # Voting consolidation every 3 cycles
        print("\nVoting consolidation every 3 cycles:")
        for cycles in [3, 6, 12, 30]:
            acc = self.test_voting_consolidation(cycles, 3)
            results[f"consol3_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # Voting consolidation every cycle
        print("\nVoting consolidation every cycle:")
        for cycles in [5, 10, 30, 100]:
            acc = self.test_voting_consolidation(cycles, 1)
            results[f"consol1_{cycles}"] = acc
            print(f"  {cycles} cycles: {acc*100:.0f}%")

        # Analysis
        print("\nConsolidation Effect:")
        baseline_10 = results["baseline_10"]
        consol_10 = results.get("consol3_12", 0)
        print(f"  ~10 cycles: {baseline_10*100:.0f}% (baseline) vs {consol_10*100:.0f}% (consol)")

        return results

if __name__ == "__main__":
    exp = VotingConsolidation()
    results = exp.run()

    output = {
        "cycle": 2040,
        "experiment": "Voting Consolidation",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2040_voting_consolidation.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
