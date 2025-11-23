"""
Cycle 2026: Storage Capacity Under Noise
========================================
C2004 found ~5 item capacity at d=2048 without noise.
How does noise affect this capacity?

Hypothesis: Noise reduces effective capacity.
"""

import numpy as np
import json
from datetime import datetime

class CapacityUnderNoise:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 30
        self.num_items_range = range(2, 9)
        self.noise_levels = [0.0, 0.5, 1.0, 1.5]

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

    def add_noise(self, v, noise_level):
        if noise_level == 0:
            return v
        noise = np.random.normal(0, noise_level/np.sqrt(self.d), self.d)
        return self._normalize(v + noise)

    def test_capacity(self, num_items, noise_level):
        correct = 0

        for _ in range(self.num_trials):
            # Create items
            items = [self._generate() for _ in range(num_items)]

            # Create positions
            np.random.seed(42)
            positions = [self._normalize(np.random.randn(self.d)) for _ in range(num_items)]
            np.random.seed(None)

            # Build memory trace
            trace = np.zeros(self.d)
            for i, item in enumerate(items):
                trace += self._circ_conv(positions[i], item)
            trace = self._normalize(trace)
            trace = self.add_noise(trace, noise_level)

            # Test retrieval of random item
            test_idx = np.random.randint(num_items)
            retrieved = self._circ_corr(trace, positions[test_idx])
            retrieved = self._normalize(retrieved)

            if np.dot(retrieved, items[test_idx]) > 0.3:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2026: Storage Capacity Under Noise")
        print("-" * 60)

        results = []

        # Header
        header = f"{'Items':>6}"
        for nl in self.noise_levels:
            header += f" | noise={nl:<4}"
        print(header)
        print("-" * 60)

        for num_items in self.num_items_range:
            row = f"{num_items:>6}"
            item_results = {"num_items": num_items, "accuracies": {}}

            for nl in self.noise_levels:
                acc = self.test_capacity(num_items, nl)
                row += f" | {acc*100:>8.0f}%"
                item_results["accuracies"][str(nl)] = acc

            results.append(item_results)
            print(row)

        print()
        # Find capacity limits
        print("Capacity Limits (>90% accuracy):")
        for nl in self.noise_levels:
            capacity = 0
            for r in results:
                if r["accuracies"][str(nl)] >= 0.9:
                    capacity = r["num_items"]
                else:
                    break
            print(f"  noise={nl}: {capacity} items")

        return results

if __name__ == "__main__":
    exp = CapacityUnderNoise()
    results = exp.run()

    output = {
        "cycle": 2026,
        "experiment": "Capacity Under Noise",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2026_capacity_under_noise.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
