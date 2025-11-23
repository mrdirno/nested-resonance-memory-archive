"""
Cycle 2032: Error Correction via Redundancy
==========================================
Test if redundant encoding improves robustness under noise.

Method: Store each item multiple times with different positions.
Retrieve from all and combine.
"""

import numpy as np
import json
from datetime import datetime

class ErrorCorrection:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.noise_levels = [1.0, 2.0, 3.0]
        self.redundancies = [1, 2, 3, 5]

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
        noise = np.random.normal(0, noise_level/np.sqrt(self.d), self.d)
        return self._normalize(v + noise)

    def test_condition(self, redundancy, noise_level):
        correct = 0

        for _ in range(self.num_trials):
            # Create item and positions
            item = self._generate()
            positions = [self._generate() for _ in range(redundancy)]

            # Build trace with redundant encoding
            trace = np.zeros(self.d)
            for pos in positions:
                trace += self._circ_conv(pos, item)
            trace = self._normalize(trace)
            trace = self.add_noise(trace, noise_level)

            # Retrieve from all positions and combine
            retrieved_sum = np.zeros(self.d)
            for pos in positions:
                r = self._circ_corr(trace, pos)
                retrieved_sum += r
            retrieved = self._normalize(retrieved_sum)

            if np.dot(retrieved, item) > 0.3:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2032: Error Correction via Redundancy")
        print("-" * 60)

        results = []

        # Header
        header = f"{'Redund':>6}"
        for nl in self.noise_levels:
            header += f" | noise={nl:.1f}"
        print(header)
        print("-" * 60)

        for red in self.redundancies:
            row = f"{red:>6}"
            red_results = {"redundancy": red, "accuracies": {}}

            for nl in self.noise_levels:
                acc = self.test_condition(red, nl)
                row += f" | {acc*100:>7.0f}%"
                red_results["accuracies"][str(nl)] = acc

            results.append(red_results)
            print(row)

        print()
        # Analysis
        print("Error Correction Analysis:")
        for nl in self.noise_levels:
            accs = [r["accuracies"][str(nl)] for r in results]
            if accs[-1] > accs[0]:
                improvement = (accs[-1] - accs[0]) * 100
                print(f"  noise={nl}: Redundancy helps ({improvement:+.0f}% improvement)")
            else:
                print(f"  noise={nl}: No improvement from redundancy")

        return results

if __name__ == "__main__":
    exp = ErrorCorrection()
    results = exp.run()

    output = {
        "cycle": 2032,
        "experiment": "Error Correction via Redundancy",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2032_error_correction.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
