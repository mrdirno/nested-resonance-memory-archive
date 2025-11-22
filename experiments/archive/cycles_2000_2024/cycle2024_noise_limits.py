"""
Cycle 2024: Finding Noise Limits
================================
C2023 showed 100% robustness up to noise=1.0.
Push further to find actual degradation points.

Test: Higher noise levels (1.0 to 10.0)
"""

import numpy as np
import json
from datetime import datetime

class NoiseLimits:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.noise_levels = [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]

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

    def run(self):
        print("Cycle 2024: Finding Noise Limits")
        print("-" * 50)

        results = []

        print(f"{'Noise':>6} | {'Bind/Unbind':>12} | {'Sequence':>10} | {'Composition':>12}")
        print("-" * 50)

        for noise_level in self.noise_levels:
            correct_bind = 0
            correct_seq = 0
            correct_comp = 0

            for _ in range(self.num_trials):
                # Test 1: Bind/Unbind
                A = self._generate()
                B = self._generate()
                AB = self._circ_conv(A, B)
                AB_noisy = self.add_noise(AB, noise_level)
                retrieved = self._circ_corr(AB_noisy, A)
                retrieved = self._normalize(retrieved)
                if np.dot(retrieved, B) > 0.3:
                    correct_bind += 1

                # Test 2: Sequence (3 items)
                items = [self._generate() for _ in range(3)]
                np.random.seed(42)
                positions = [self._normalize(np.random.randn(self.d)) for _ in range(3)]
                np.random.seed(None)

                trace = np.zeros(self.d)
                for i, item in enumerate(items):
                    trace += self._circ_conv(positions[i], item)
                trace = self._normalize(trace)
                trace_noisy = self.add_noise(trace, noise_level)

                retrieved = self._circ_corr(trace_noisy, positions[1])
                retrieved = self._normalize(retrieved)
                if np.dot(retrieved, items[1]) > 0.3:
                    correct_seq += 1

                # Test 3: Composition
                C = self._generate()
                AB_sum = self._normalize(A + B)
                comp_rule = self._circ_conv(AB_sum, C)
                comp_noisy = self.add_noise(comp_rule, noise_level)
                predicted = self._circ_corr(comp_noisy, AB_sum)
                predicted = self._normalize(predicted)
                if np.dot(predicted, C) > 0.3:
                    correct_comp += 1

            acc_bind = correct_bind / self.num_trials
            acc_seq = correct_seq / self.num_trials
            acc_comp = correct_comp / self.num_trials

            results.append({
                "noise_level": noise_level,
                "bind_accuracy": acc_bind,
                "sequence_accuracy": acc_seq,
                "composition_accuracy": acc_comp
            })

            print(f"{noise_level:>6.1f} | {acc_bind*100:>11.0f}% | {acc_seq*100:>9.0f}% | {acc_comp*100:>11.0f}%")

        print()
        # Find degradation points
        for op_name, op_key in [("Bind", "bind_accuracy"), ("Sequence", "sequence_accuracy"), ("Composition", "composition_accuracy")]:
            for r in results:
                if r[op_key] < 0.9:
                    print(f"{op_name} 90% threshold at noise: {r['noise_level']}")
                    break
            else:
                print(f"{op_name}: Still >90% at noise=10.0!")

        return results

if __name__ == "__main__":
    exp = NoiseLimits()
    results = exp.run()

    output = {
        "cycle": 2024,
        "experiment": "Noise Limits",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2024_noise_limits.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
