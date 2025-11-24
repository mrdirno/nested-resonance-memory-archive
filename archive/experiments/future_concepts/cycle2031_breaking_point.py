"""
Cycle 2031: Finding the Breaking Point
======================================
Push beyond C2030 limits to find actual failure.
"""

import numpy as np
import json
from datetime import datetime

class BreakingPoint:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 30

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

    def add_noise(self, v, noise_level):
        if noise_level == 0:
            return v
        noise = np.random.normal(0, noise_level/np.sqrt(self.d), self.d)
        return self._normalize(v + noise)

    def test_condition(self, num_items, similarity, noise_level):
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
            trace = self.add_noise(trace, noise_level)

            retrieved = self._circ_corr(trace, positions[0])
            retrieved = self._normalize(retrieved)

            similarities = [np.dot(retrieved, item) for item in items]
            if np.argmax(similarities) == 0:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2031: Finding the Breaking Point")
        print("-" * 70)

        # Extreme scenarios
        scenarios = [
            (6, 0.95, 1.5, "Extreme 1"),
            (8, 0.9, 1.5, "Extreme 2"),
            (6, 0.99, 1.0, "Max similarity"),
            (6, 0.95, 2.0, "Max noise"),
            (8, 0.99, 1.5, "Combined extreme"),
            (10, 0.9, 1.5, "High capacity extreme"),
            (6, 0.99, 2.0, "Double extreme"),
        ]

        results = []

        print(f"{'Scenario':<22} | {'Items':>5} | {'Sim':>5} | {'Noise':>5} | {'Accuracy':>10}")
        print("-" * 70)

        for items, sim, noise, label in scenarios:
            acc = self.test_condition(items, sim, noise)
            results.append({
                "label": label,
                "num_items": items,
                "similarity": sim,
                "noise": noise,
                "accuracy": acc
            })
            print(f"{label:<22} | {items:>5} | {sim:>5.2f} | {noise:>5.1f} | {acc*100:>9.0f}%")

        print()
        # Analysis
        print("Breaking Point Analysis:")
        for r in results:
            if r["accuracy"] < 0.5:
                print(f"  BROKEN: {r['label']} ({r['accuracy']*100:.0f}%)")
            elif r["accuracy"] < 0.9:
                print(f"  Degraded: {r['label']} ({r['accuracy']*100:.0f}%)")

        return results

if __name__ == "__main__":
    exp = BreakingPoint()
    results = exp.run()

    output = {
        "cycle": 2031,
        "experiment": "Breaking Point",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2031_breaking_point.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
