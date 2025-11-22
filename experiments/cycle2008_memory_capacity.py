"""
Cycle 2008: Memory Capacity Test
================================
We've characterized inference depth. Now test storage capacity.

Question: How many items can be stored and retrieved from a
superposition (holographic memory)?

Classic result: ~sqrt(d) items at d dimensions with good retrieval.

Method: Store N items as superposition, test retrieval accuracy.
"""

import numpy as np
import json
from datetime import datetime

class MemoryCapacity:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 30
        self.n_items_list = [1, 2, 5, 10, 20, 50, 100, 200]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def test_capacity(self, n_items):
        """Test retrieval accuracy for n_items stored."""
        correct = 0
        total_sim = 0.0

        for _ in range(self.num_trials):
            # Generate n_items key-value pairs
            keys = [self.generate() for _ in range(n_items)]
            values = [self.generate() for _ in range(n_items)]

            # Create memory as superposition of bound pairs
            memory = np.zeros(self.d)
            for k, v in zip(keys, values):
                bound = np.real(np.fft.ifft(np.fft.fft(k) * np.fft.fft(v)))
                memory += bound

            # Test retrieval of each item
            item_correct = 0
            item_sim = 0.0

            for i in range(n_items):
                # Retrieve value for key i
                retrieved = np.real(np.fft.ifft(
                    np.fft.fft(memory) * np.conj(np.fft.fft(keys[i]))))
                retrieved = self._normalize(retrieved)

                sim = np.dot(retrieved, values[i])
                item_sim += sim

                if sim > 0.3:
                    item_correct += 1

            # Average over items
            accuracy = item_correct / n_items
            avg_sim = item_sim / n_items

            if accuracy > 0.8:
                correct += 1
            total_sim += avg_sim

        return correct / self.num_trials, total_sim / self.num_trials

    def run(self):
        print("Cycle 2008: Memory Capacity Test")
        print("-" * 50)
        print(f"Dimension: {self.d}")
        print(f"Theoretical capacity: ~sqrt({self.d}) = {int(np.sqrt(self.d))}")
        print()

        results = []

        print(f"{'N Items':>8} | {'Accuracy':>10} | {'Similarity':>10}")
        print("-" * 35)

        for n in self.n_items_list:
            acc, sim = self.test_capacity(n)
            results.append({
                "n_items": n,
                "accuracy": acc,
                "similarity": sim
            })
            status = "✓" if acc > 0.8 else "✗" if acc < 0.5 else "~"
            print(f"{n:>8} | {acc*100:>9.1f}% | {sim:>10.4f} {status}")

        print()

        # Find capacity
        capacity = 0
        for r in results:
            if r["accuracy"] > 0.8:
                capacity = r["n_items"]
            else:
                break

        print(f"Practical capacity (>80% accuracy): {capacity} items")
        print(f"Theoretical: sqrt({self.d}) = {int(np.sqrt(self.d))}")

        return results

if __name__ == "__main__":
    exp = MemoryCapacity()
    results = exp.run()

    output = {
        "cycle": 2008,
        "experiment": "Memory Capacity",
        "timestamp": datetime.now().isoformat(),
        "dimension": 2048,
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2008_memory_capacity.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
