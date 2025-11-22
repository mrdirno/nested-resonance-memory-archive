"""
Cycle 2025: Dimensional Scaling of Noise Robustness
===================================================
How does noise robustness scale with dimension?

Hypothesis: Higher dimensions provide better noise immunity.
Test: Same noise levels across dimensions 256-8192.
"""

import numpy as np
import json
from datetime import datetime

class DimensionNoiseScaling:
    def __init__(self):
        self.dimensions = [256, 512, 1024, 2048, 4096, 8192]
        self.noise_levels = [1.0, 2.0, 3.0]
        self.num_trials = 30

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

    def add_noise(self, v, noise_level, d):
        noise = np.random.normal(0, noise_level/np.sqrt(d), d)
        return self._normalize(v + noise)

    def test_bind(self, d, noise_level):
        correct = 0
        for _ in range(self.num_trials):
            A = self._generate(d)
            B = self._generate(d)
            AB = self._circ_conv(A, B)
            AB_noisy = self.add_noise(AB, noise_level, d)
            retrieved = self._circ_corr(AB_noisy, A)
            retrieved = self._normalize(retrieved)
            if np.dot(retrieved, B) > 0.3:
                correct += 1
        return correct / self.num_trials

    def run(self):
        print("Cycle 2025: Dimensional Scaling of Noise Robustness")
        print("-" * 60)

        results = []

        # Header
        header = f"{'Dim':>6}"
        for nl in self.noise_levels:
            header += f" | noise={nl:<4}"
        print(header)
        print("-" * 60)

        for d in self.dimensions:
            row = f"{d:>6}"
            dim_results = {"dimension": d, "accuracies": {}}

            for nl in self.noise_levels:
                acc = self.test_bind(d, nl)
                row += f" | {acc*100:>8.0f}%"
                dim_results["accuracies"][str(nl)] = acc

            results.append(dim_results)
            print(row)

        print()
        # Analysis
        print("Scaling Analysis:")
        for nl in self.noise_levels:
            accs = [r["accuracies"][str(nl)] for r in results]
            if accs[0] < accs[-1]:
                print(f"  noise={nl}: Higher dim = better robustness ({accs[0]*100:.0f}% -> {accs[-1]*100:.0f}%)")
            else:
                print(f"  noise={nl}: Dimension-independent ({accs[0]*100:.0f}% -> {accs[-1]*100:.0f}%)")

        return results

if __name__ == "__main__":
    exp = DimensionNoiseScaling()
    results = exp.run()

    output = {
        "cycle": 2025,
        "experiment": "Dimension Noise Scaling",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2025_dimension_noise_scaling.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
