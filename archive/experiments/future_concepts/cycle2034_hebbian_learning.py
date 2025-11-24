"""
Cycle 2034: Hebbian-like Learning
=================================
Test if repeated retrieval strengthens associations.

Method: Repeatedly query and reinforce the trace.
"""

import numpy as np
import json
from datetime import datetime

class HebbianLearning:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.learning_rates = [0.0, 0.1, 0.3, 0.5]
        self.num_iterations = [1, 3, 5, 10]

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

    def test_learning(self, learning_rate, num_iters):
        similarities = []
        noise_level = 2.0  # Start with degraded condition

        for _ in range(self.num_trials):
            item = self._generate()
            position = self._generate()

            # Initial noisy trace
            trace = self._circ_conv(position, item)
            trace = self._normalize(trace)
            trace = self.add_noise(trace, noise_level)

            # Learning iterations
            for _ in range(num_iters):
                # Retrieve
                retrieved = self._circ_corr(trace, position)
                retrieved = self._normalize(retrieved)

                # Reinforce (Hebbian update)
                if learning_rate > 0:
                    reinforcement = self._circ_conv(position, retrieved)
                    trace = trace + learning_rate * reinforcement
                    trace = self._normalize(trace)

            # Final retrieval
            final = self._circ_corr(trace, position)
            final = self._normalize(final)
            sim = np.dot(final, item)
            similarities.append(sim)

        return np.mean(similarities), np.std(similarities)

    def run(self):
        print("Cycle 2034: Hebbian-like Learning")
        print("-" * 70)

        results = []

        print(f"{'LR':>6} | {'1 iter':>12} | {'3 iter':>12} | {'5 iter':>12} | {'10 iter':>12}")
        print("-" * 70)

        for lr in self.learning_rates:
            row = f"{lr:>6.1f}"
            lr_results = {"learning_rate": lr, "similarities": {}}

            for n_iter in self.num_iterations:
                mean_sim, std_sim = self.test_learning(lr, n_iter)
                row += f" | {mean_sim:.3f}±{std_sim:.3f}"
                lr_results["similarities"][str(n_iter)] = {"mean": mean_sim, "std": std_sim}

            results.append(lr_results)
            print(row)

        print()
        # Analysis
        print("Learning Analysis (at 10 iterations):")
        baseline = results[0]["similarities"]["10"]["mean"]
        for r in results[1:]:
            lr = r["learning_rate"]
            final = r["similarities"]["10"]["mean"]
            change = (final - baseline) * 100
            print(f"  LR={lr}: {change:+.1f}% vs baseline")

        return results

if __name__ == "__main__":
    exp = HebbianLearning()
    results = exp.run()

    output = {
        "cycle": 2034,
        "experiment": "Hebbian Learning",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2034_hebbian_learning.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
