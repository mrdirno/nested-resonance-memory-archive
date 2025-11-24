"""
Cycle 2028: Extreme Interference Conditions
===========================================
C2027 showed 100% robustness up to similarity=0.8.
Push further with extreme similarity and more items.
"""

import numpy as np
import json
from datetime import datetime

class ExtremeInterference:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.similarities = [0.8, 0.9, 0.95, 0.99]
        self.num_items_range = [4, 5, 6, 7]

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

            retrieved = self._circ_corr(trace, positions[0])
            retrieved = self._normalize(retrieved)

            if np.dot(retrieved, items[0]) > 0.3:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2028: Extreme Interference Conditions")
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
        # Find failure points
        print("Failure Analysis (first <90%):")
        for n in self.num_items_range:
            for r in results:
                if r["accuracies"][str(n)] < 0.9:
                    print(f"  {n} items: fails at similarity={r['similarity']}")
                    break
            else:
                print(f"  {n} items: robust even at similarity=0.99")

        return results

if __name__ == "__main__":
    exp = ExtremeInterference()
    results = exp.run()

    output = {
        "cycle": 2028,
        "experiment": "Extreme Interference",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2028_extreme_interference.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
