"""
Cycle 2027: Interference Patterns
=================================
Test how similar items interfere with retrieval.

Question: Does storing similar items degrade retrieval?
Method: Create items with controlled similarity and test retrieval.
"""

import numpy as np
import json
from datetime import datetime

class InterferencePatterns:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.similarities = [0.0, 0.2, 0.4, 0.6, 0.8]

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
        """Create vector with controlled similarity to v."""
        noise = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        noise = self._normalize(noise)
        # Linear interpolation
        result = similarity * v + np.sqrt(1 - similarity**2) * noise
        return self._normalize(result)

    def run(self):
        print("Cycle 2027: Interference Patterns")
        print("-" * 50)

        results = []

        print(f"{'Similarity':>10} | {'2 items':>10} | {'3 items':>10} | {'4 items':>10}")
        print("-" * 50)

        for sim in self.similarities:
            sim_results = {"similarity": sim}

            for num_items in [2, 3, 4]:
                correct = 0

                for _ in range(self.num_trials):
                    # Create base item and similar items
                    base = self._generate()
                    items = [base] + [self.create_similar(base, sim) for _ in range(num_items - 1)]

                    # Create positions
                    np.random.seed(42)
                    positions = [self._normalize(np.random.randn(self.d)) for _ in range(num_items)]
                    np.random.seed(None)

                    # Build trace
                    trace = np.zeros(self.d)
                    for i, item in enumerate(items):
                        trace += self._circ_conv(positions[i], item)
                    trace = self._normalize(trace)

                    # Retrieve first item
                    retrieved = self._circ_corr(trace, positions[0])
                    retrieved = self._normalize(retrieved)

                    if np.dot(retrieved, items[0]) > 0.3:
                        correct += 1

                acc = correct / self.num_trials
                sim_results[f"{num_items}_items"] = acc

            results.append(sim_results)
            print(f"{sim:>10.1f} | {sim_results['2_items']*100:>9.0f}% | {sim_results['3_items']*100:>9.0f}% | {sim_results['4_items']*100:>9.0f}%")

        print()
        # Analysis
        print("Interference Analysis:")
        for num_items in [2, 3, 4]:
            key = f"{num_items}_items"
            accs = [r[key] for r in results]
            if accs[0] > accs[-1]:
                print(f"  {num_items} items: Interference increases with similarity ({accs[0]*100:.0f}% -> {accs[-1]*100:.0f}%)")
            else:
                print(f"  {num_items} items: No interference effect ({accs[0]*100:.0f}% -> {accs[-1]*100:.0f}%)")

        return results

if __name__ == "__main__":
    exp = InterferencePatterns()
    results = exp.run()

    output = {
        "cycle": 2027,
        "experiment": "Interference Patterns",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2027_interference_patterns.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
