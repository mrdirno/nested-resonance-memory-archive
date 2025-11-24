"""
Cycle 2042: Extended Capacity Test
==================================
Test beyond 19 items to find true capacity limits.
"""

import numpy as np
import json
from datetime import datetime

class ExtendedCapacity:
    def __init__(self):
        self.num_trials = 100
        self.dimensions = [512, 1024, 2048, 4096]
        self.item_counts = [10, 20, 30, 50, 75, 100]

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

    def test_capacity(self, d, num_items):
        correct = 0

        for _ in range(self.num_trials):
            items = [self._generate(d) for _ in range(num_items)]
            np.random.seed(42)
            positions = [self._normalize(np.random.randn(d)) for _ in range(num_items)]
            np.random.seed(None)

            trace = np.zeros(d)
            for i, item in enumerate(items):
                trace += self._circ_conv(positions[i], item)
            trace = self._normalize(trace)

            test_idx = np.random.randint(num_items)
            retrieved = self._circ_corr(trace, positions[test_idx])
            retrieved = self._normalize(retrieved)

            sims = [np.dot(retrieved, item) for item in items]
            if np.argmax(sims) == test_idx:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2042: Extended Capacity Test")
        print("-" * 70)

        results = []

        # Header
        header = f"{'Items':>6}"
        for d in self.dimensions:
            header += f" | d={d:<5}"
        print(header)
        print("-" * 70)

        for n_items in self.item_counts:
            row = f"{n_items:>6}"
            item_results = {"num_items": n_items, "accuracies": {}}

            for d in self.dimensions:
                acc = self.test_capacity(d, n_items)
                row += f" | {acc*100:>6.0f}%"
                item_results["accuracies"][str(d)] = acc

            results.append(item_results)
            print(row)

        print()
        # Find 90% threshold for each dimension
        print("Capacity at 90% accuracy:")
        for d in self.dimensions:
            for r in results:
                if r["accuracies"][str(d)] < 0.9:
                    capacity = r["num_items"]
                    print(f"  d={d}: ~{capacity} items")
                    break
            else:
                print(f"  d={d}: >100 items")

        return results

if __name__ == "__main__":
    exp = ExtendedCapacity()
    results = exp.run()

    output = {
        "cycle": 2042,
        "experiment": "Extended Capacity",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2042_extended_capacity.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
