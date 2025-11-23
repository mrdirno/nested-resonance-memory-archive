"""
Cycle 2035: Gated Reinforcement Learning
========================================
Only reinforce when retrieval confidence is high.
Gate based on similarity threshold.
"""

import numpy as np
import json
from datetime import datetime

class GatedLearning:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.thresholds = [0.0, 0.3, 0.5, 0.7]
        self.learning_rate = 0.3

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

    def test_gated(self, threshold, num_iters=10):
        similarities = []
        reinforcements = []
        noise_level = 2.0

        for _ in range(self.num_trials):
            item = self._generate()
            position = self._generate()

            trace = self._circ_conv(position, item)
            trace = self._normalize(trace)
            trace = self.add_noise(trace, noise_level)

            reinforce_count = 0

            for _ in range(num_iters):
                retrieved = self._circ_corr(trace, position)
                retrieved_norm = self._normalize(retrieved)

                # Estimate confidence (max activation)
                confidence = np.max(np.abs(retrieved_norm))

                # Gated reinforcement
                if confidence > threshold:
                    reinforcement = self._circ_conv(position, retrieved_norm)
                    trace = trace + self.learning_rate * reinforcement
                    trace = self._normalize(trace)
                    reinforce_count += 1

            final = self._circ_corr(trace, position)
            final = self._normalize(final)
            sim = np.dot(final, item)
            similarities.append(sim)
            reinforcements.append(reinforce_count)

        return np.mean(similarities), np.mean(reinforcements)

    def run(self):
        print("Cycle 2035: Gated Reinforcement Learning")
        print("-" * 60)

        results = []

        print(f"{'Threshold':>10} | {'Similarity':>12} | {'Reinforcements':>15}")
        print("-" * 60)

        # Baseline (no learning)
        base_sim, _ = self.test_gated(threshold=float('inf'))
        print(f"{'Baseline':>10} | {base_sim:.3f}        | {0:>15}")
        results.append({"threshold": "baseline", "similarity": base_sim, "reinforcements": 0})

        for thresh in self.thresholds:
            sim, reinf = self.test_gated(thresh)
            results.append({"threshold": thresh, "similarity": sim, "reinforcements": reinf})
            print(f"{thresh:>10.1f} | {sim:.3f}        | {reinf:>15.1f}")

        print()
        # Analysis
        print("Gating Analysis:")
        for r in results[1:]:
            change = (r["similarity"] - base_sim) * 100
            print(f"  threshold={r['threshold']}: {change:+.1f}% ({r['reinforcements']:.0f} reinforcements)")

        return results

if __name__ == "__main__":
    exp = GatedLearning()
    results = exp.run()

    output = {
        "cycle": 2035,
        "experiment": "Gated Learning",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2035_gated_learning.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
