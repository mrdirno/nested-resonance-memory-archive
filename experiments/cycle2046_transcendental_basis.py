"""
Cycle 2046: Transcendental Basis Holographic Memory
===================================================
Test holographic memory using transcendental-based vectors (π, e, φ).
Compare with random Gaussian basis.

Hypothesis: Transcendental basis may have different capacity/robustness.
"""

import numpy as np
import json
from datetime import datetime

class TranscendentalBasis:
    def __init__(self):
        self.dimensions = [256, 512, 1024]
        self.num_trials = 50

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_gaussian(self, d):
        """Standard Gaussian random vector."""
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def generate_transcendental(self, d, seed=None):
        """Generate vector using transcendental oscillators."""
        if seed is not None:
            np.random.seed(seed)

        # Use π, e, φ as base frequencies
        pi_freq = np.pi
        e_freq = np.e
        phi_freq = (1 + np.sqrt(5)) / 2  # Golden ratio

        t = np.arange(d) / d

        # Random phases
        phase1 = np.random.random() * 2 * np.pi
        phase2 = np.random.random() * 2 * np.pi
        phase3 = np.random.random() * 2 * np.pi

        # Combine transcendental oscillators
        v = (np.sin(2 * pi_freq * t * np.random.randint(1, 10) + phase1) +
             np.cos(2 * e_freq * t * np.random.randint(1, 10) + phase2) +
             np.sin(2 * phi_freq * t * np.random.randint(1, 10) + phase3))

        if seed is not None:
            np.random.seed(None)

        return self._normalize(v)

    def test_capacity(self, d, generate_func, num_items):
        """Test discrimination capacity."""
        correct = 0

        for _ in range(self.num_trials):
            items = [generate_func(d) for _ in range(num_items)]
            positions = [generate_func(d) for _ in range(num_items)]

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
        print("Cycle 2046: Transcendental Basis Holographic Memory")
        print("-" * 70)

        results = []

        print(f"{'Dim':>6} | {'Type':>15} | {'10 items':>10} | {'30 items':>10} | {'50 items':>10}")
        print("-" * 70)

        for d in self.dimensions:
            # Gaussian baseline
            gauss_10 = self.test_capacity(d, self.generate_gaussian, 10)
            gauss_30 = self.test_capacity(d, self.generate_gaussian, 30)
            gauss_50 = self.test_capacity(d, self.generate_gaussian, 50)

            results.append({
                "dimension": d,
                "type": "Gaussian",
                "10_items": gauss_10,
                "30_items": gauss_30,
                "50_items": gauss_50
            })

            print(f"{d:>6} | {'Gaussian':>15} | {gauss_10*100:>9.0f}% | {gauss_30*100:>9.0f}% | {gauss_50*100:>9.0f}%")

            # Transcendental
            trans_10 = self.test_capacity(d, self.generate_transcendental, 10)
            trans_30 = self.test_capacity(d, self.generate_transcendental, 30)
            trans_50 = self.test_capacity(d, self.generate_transcendental, 50)

            results.append({
                "dimension": d,
                "type": "Transcendental",
                "10_items": trans_10,
                "30_items": trans_30,
                "50_items": trans_50
            })

            print(f"{d:>6} | {'Transcendental':>15} | {trans_10*100:>9.0f}% | {trans_30*100:>9.0f}% | {trans_50*100:>9.0f}%")

        print()
        # Analysis
        print("Comparison (50 items, d=1024):")
        gauss = [r for r in results if r["dimension"] == 1024 and r["type"] == "Gaussian"][0]["50_items"]
        trans = [r for r in results if r["dimension"] == 1024 and r["type"] == "Transcendental"][0]["50_items"]
        diff = (trans - gauss) * 100
        print(f"  Gaussian: {gauss*100:.0f}%")
        print(f"  Transcendental: {trans*100:.0f}%")
        print(f"  Difference: {diff:+.1f}%")

        return results

if __name__ == "__main__":
    exp = TranscendentalBasis()
    results = exp.run()

    output = {
        "cycle": 2046,
        "experiment": "Transcendental Basis",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2046_transcendental_basis.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
