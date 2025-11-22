"""
Cycle 2030: Combined Stress Test
================================
Test combined effects of noise, similarity, and capacity.
Find operational envelope for holographic memory.
"""

import numpy as np
import json
from datetime import datetime

class CombinedStress:
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
            if similarity > 0:
                items = [base] + [self.create_similar(base, similarity) for _ in range(num_items - 1)]
            else:
                items = [self._generate() for _ in range(num_items)]

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

            # Discrimination test
            similarities = [np.dot(retrieved, item) for item in items]
            if np.argmax(similarities) == 0:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2030: Combined Stress Test")
        print("-" * 70)

        # Test scenarios
        scenarios = [
            # (items, similarity, noise) - label
            (4, 0.0, 0.0, "Baseline"),
            (6, 0.0, 0.0, "High capacity"),
            (4, 0.5, 0.0, "Medium similarity"),
            (4, 0.0, 1.0, "Medium noise"),
            (4, 0.5, 1.0, "Sim + Noise"),
            (6, 0.5, 1.0, "All stress"),
            (4, 0.9, 1.0, "High sim + noise"),
            (6, 0.9, 1.0, "Max stress"),
        ]

        results = []

        print(f"{'Scenario':<20} | {'Items':>5} | {'Sim':>5} | {'Noise':>5} | {'Accuracy':>10}")
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
            print(f"{label:<20} | {items:>5} | {sim:>5.1f} | {noise:>5.1f} | {acc*100:>9.0f}%")

        print()
        # Summary
        print("Operational Envelope:")
        safe = [r for r in results if r["accuracy"] >= 0.9]
        if safe:
            print(f"  Safe conditions (≥90%): {len(safe)}/{len(results)}")
        degraded = [r for r in results if 0.5 <= r["accuracy"] < 0.9]
        if degraded:
            print(f"  Degraded (50-90%): {len(degraded)}/{len(results)}")
        failed = [r for r in results if r["accuracy"] < 0.5]
        if failed:
            print(f"  Failed (<50%): {len(failed)}/{len(results)}")

        return results

if __name__ == "__main__":
    exp = CombinedStress()
    results = exp.run()

    output = {
        "cycle": 2030,
        "experiment": "Combined Stress Test",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2030_combined_stress.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
