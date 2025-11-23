"""
Cycle 2047: Orthogonalized Transcendental Basis
===============================================
Fix C2046 failure by orthogonalizing transcendental vectors.
Use Gram-Schmidt or QR decomposition on transcendental base.
"""

import numpy as np
import json
from datetime import datetime

class OrthogonalTranscendental:
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
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def generate_transcendental_base(self, d):
        """Generate raw transcendental vector."""
        pi_freq = np.pi
        e_freq = np.e
        phi_freq = (1 + np.sqrt(5)) / 2

        t = np.arange(d) / d

        phase1 = np.random.random() * 2 * np.pi
        phase2 = np.random.random() * 2 * np.pi
        phase3 = np.random.random() * 2 * np.pi

        v = (np.sin(2 * pi_freq * t * np.random.randint(1, 10) + phase1) +
             np.cos(2 * e_freq * t * np.random.randint(1, 10) + phase2) +
             np.sin(2 * phi_freq * t * np.random.randint(1, 10) + phase3))

        return v

    def generate_orthogonal_set(self, d, n, base_generator):
        """Generate n orthogonal vectors using Gram-Schmidt."""
        vectors = []

        for i in range(n):
            v = base_generator(d)

            # Gram-Schmidt orthogonalization
            for u in vectors:
                v = v - np.dot(v, u) * u

            norm = np.linalg.norm(v)
            if norm > 1e-10:
                v = v / norm
                vectors.append(v)
            else:
                # Fallback to Gaussian if degenerate
                v = np.random.randn(d)
                for u in vectors:
                    v = v - np.dot(v, u) * u
                v = v / np.linalg.norm(v)
                vectors.append(v)

        return vectors

    def test_capacity(self, d, num_items, orthogonalize=False):
        """Test discrimination capacity."""
        correct = 0

        for _ in range(self.num_trials):
            if orthogonalize:
                # Generate orthogonal transcendental vectors
                items = self.generate_orthogonal_set(d, num_items, self.generate_transcendental_base)
                positions = self.generate_orthogonal_set(d, num_items, self.generate_transcendental_base)
            else:
                # Raw Gaussian (baseline)
                items = [self.generate_gaussian(d) for _ in range(num_items)]
                positions = [self.generate_gaussian(d) for _ in range(num_items)]

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
        print("Cycle 2047: Orthogonalized Transcendental Basis")
        print("-" * 70)

        results = []

        print(f"{'Dim':>6} | {'Type':>20} | {'10 items':>10} | {'30 items':>10} | {'50 items':>10}")
        print("-" * 70)

        for d in self.dimensions:
            # Gaussian baseline
            gauss_10 = self.test_capacity(d, 10, orthogonalize=False)
            gauss_30 = self.test_capacity(d, 30, orthogonalize=False)
            gauss_50 = self.test_capacity(d, 50, orthogonalize=False)

            results.append({
                "dimension": d,
                "type": "Gaussian",
                "10": gauss_10, "30": gauss_30, "50": gauss_50
            })

            print(f"{d:>6} | {'Gaussian':>20} | {gauss_10*100:>9.0f}% | {gauss_30*100:>9.0f}% | {gauss_50*100:>9.0f}%")

            # Orthogonalized transcendental
            orth_10 = self.test_capacity(d, 10, orthogonalize=True)
            orth_30 = self.test_capacity(d, 30, orthogonalize=True)
            orth_50 = self.test_capacity(d, 50, orthogonalize=True)

            results.append({
                "dimension": d,
                "type": "Orth-Transcendental",
                "10": orth_10, "30": orth_30, "50": orth_50
            })

            print(f"{d:>6} | {'Orth-Transcendental':>20} | {orth_10*100:>9.0f}% | {orth_30*100:>9.0f}% | {orth_50*100:>9.0f}%")

        print()
        # Analysis
        print("C2046 vs C2047 (50 items, d=1024):")
        gauss = [r for r in results if r["dimension"] == 1024 and r["type"] == "Gaussian"][0]["50"]
        orth = [r for r in results if r["dimension"] == 1024 and r["type"] == "Orth-Transcendental"][0]["50"]
        print(f"  C2046 Raw Transcendental: 4%")
        print(f"  C2047 Orthogonalized: {orth*100:.0f}%")
        print(f"  Gaussian baseline: {gauss*100:.0f}%")

        recovery = (orth - 0.04) / (gauss - 0.04) * 100 if gauss > 0.04 else 0
        print(f"  Recovery: {recovery:.0f}% of Gaussian performance")

        return results

if __name__ == "__main__":
    exp = OrthogonalTranscendental()
    results = exp.run()

    output = {
        "cycle": 2047,
        "experiment": "Orthogonal Transcendental",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2047_orthogonal_transcendental.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
