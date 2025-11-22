"""
Cycle 2029: True Discrimination Test
=====================================
Test if retrieval produces BEST match to target among similar items.
Not just "similar enough" but "most similar".
"""

import numpy as np
import json
from datetime import datetime

class DiscriminationTest:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.similarities = [0.8, 0.9, 0.95, 0.99]
        self.num_items_range = [3, 4, 5, 6]

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

    def create_similar(self, v, similarity):
        noise = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        noise = self._normalize(noise)
        result = similarity * v + np.sqrt(1 - similarity**2) * noise
        return self._normalize(result)

    def test_condition(self, num_items, similarity):
        correct = 0

        for _ in range(self.num_trials):
            base = self._generate()
            items = [base] + [self.create_similar(base, similarity) for _ in range(num_items - 1)]

            np.random.seed(42)
            positions = [self._normalize(np.random.randn(self.d)) for _ in range(num_items)]
            np.random.seed(None)

            trace = np.zeros(self.d)
            for i, item in enumerate(items):
                trace += self._circ_conv(positions[i], item)
            trace = self._normalize(trace)

            # Retrieve at position 0
            retrieved = self._circ_corr(trace, positions[0])
            retrieved = self._normalize(retrieved)

            # Compare to ALL items - check if item[0] has highest similarity
            similarities = [np.dot(retrieved, item) for item in items]
            if np.argmax(similarities) == 0:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2029: True Discrimination Test")
        print("-" * 60)

        results = []

        # Header
        header = f"{'Sim':>6}"
        for n in self.num_items_range:
            header += f" | {n} items"
        print(header)
        print("-" * 60)

        for sim in self.similarities:
            row = f"{sim:>6.2f}"
            sim_results = {"similarity": sim, "accuracies": {}}

            for num_items in self.num_items_range:
                acc = self.test_condition(num_items, sim)
                row += f" | {acc*100:>6.0f}%"
                sim_results["accuracies"][str(num_items)] = acc

            results.append(sim_results)
            print(row)

        print()
        # Chance levels
        print("Chance Levels:")
        for n in self.num_items_range:
            print(f"  {n} items: {100/n:.0f}%")

        print()
        # Performance vs chance
        print("Performance vs Chance:")
        for n in self.num_items_range:
            chance = 1/n
            for r in results:
                if r["accuracies"][str(n)] < chance + 0.1:
                    print(f"  {n} items: approaches chance at similarity={r['similarity']}")
                    break
            else:
                print(f"  {n} items: well above chance at all similarities")

        return results

if __name__ == "__main__":
    exp = DiscriminationTest()
    results = exp.run()

    output = {
        "cycle": 2029,
        "experiment": "Discrimination Test",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2029_discrimination_test.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
