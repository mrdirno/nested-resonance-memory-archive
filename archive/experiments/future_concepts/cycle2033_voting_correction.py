"""
Cycle 2033: Majority Voting Error Correction
============================================
Test error correction with separate noisy traces.
Vote across retrievals instead of combining in single trace.
"""

import numpy as np
import json
from datetime import datetime

class VotingCorrection:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.noise_levels = [2.0, 3.0, 4.0]
        self.num_copies = [1, 3, 5, 7]

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

    def test_condition(self, num_copies, noise_level):
        correct = 0

        for _ in range(self.num_trials):
            # Create item
            item = self._generate()
            position = self._generate()

            # Create multiple independent noisy traces
            traces = []
            for _ in range(num_copies):
                trace = self._circ_conv(position, item)
                trace = self._normalize(trace)
                noisy_trace = self.add_noise(trace, noise_level)
                traces.append(noisy_trace)

            # Retrieve from each and average
            retrieved_sum = np.zeros(self.d)
            for trace in traces:
                r = self._circ_corr(trace, position)
                retrieved_sum += r
            retrieved = self._normalize(retrieved_sum)

            if np.dot(retrieved, item) > 0.3:
                correct += 1

        return correct / self.num_trials

    def run(self):
        print("Cycle 2033: Majority Voting Error Correction")
        print("-" * 60)

        results = []

        # Header
        header = f"{'Copies':>6}"
        for nl in self.noise_levels:
            header += f" | noise={nl:.1f}"
        print(header)
        print("-" * 60)

        for nc in self.num_copies:
            row = f"{nc:>6}"
            copy_results = {"num_copies": nc, "accuracies": {}}

            for nl in self.noise_levels:
                acc = self.test_condition(nc, nl)
                row += f" | {acc*100:>7.0f}%"
                copy_results["accuracies"][str(nl)] = acc

            results.append(copy_results)
            print(row)

        print()
        # Analysis
        print("Voting Correction Analysis:")
        for nl in self.noise_levels:
            accs = [r["accuracies"][str(nl)] for r in results]
            if accs[-1] > accs[0]:
                improvement = (accs[-1] - accs[0]) * 100
                print(f"  noise={nl}: Voting helps ({improvement:+.0f}% improvement)")
            else:
                print(f"  noise={nl}: No improvement from voting")

        return results

if __name__ == "__main__":
    exp = VotingCorrection()
    results = exp.run()

    output = {
        "cycle": 2033,
        "experiment": "Voting Error Correction",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2033_voting_correction.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
