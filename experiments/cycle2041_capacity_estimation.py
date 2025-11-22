"""
Cycle 2041: Information-Theoretic Capacity Estimation
====================================================
Estimate bits-per-dimension capacity of holographic memory.

Method: Binary classification on stored patterns.
"""

import numpy as np
import json
from datetime import datetime

class CapacityEstimation:
    def __init__(self):
        self.num_trials = 100
        self.dimensions = [128, 256, 512, 1024, 2048]

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

    def estimate_capacity(self, d):
        """Find max items that can be discriminated at 90% accuracy."""
        for num_items in range(1, 20):
            correct = 0

            for _ in range(self.num_trials):
                # Store items
                items = [self._generate(d) for _ in range(num_items)]
                np.random.seed(42)
                positions = [self._normalize(np.random.randn(d)) for _ in range(num_items)]
                np.random.seed(None)

                trace = np.zeros(d)
                for i, item in enumerate(items):
                    trace += self._circ_conv(positions[i], item)
                trace = self._normalize(trace)

                # Test retrieval
                test_idx = np.random.randint(num_items)
                retrieved = self._circ_corr(trace, positions[test_idx])
                retrieved = self._normalize(retrieved)

                # Discrimination test
                sims = [np.dot(retrieved, item) for item in items]
                if np.argmax(sims) == test_idx:
                    correct += 1

            acc = correct / self.num_trials
            if acc < 0.9:
                return num_items - 1, acc

        return 19, 1.0  # Max tested

    def run(self):
        print("Cycle 2041: Information-Theoretic Capacity Estimation")
        print("-" * 60)

        results = []

        print(f"{'Dimension':>10} | {'Capacity':>10} | {'Bits':>10} | {'Bits/dim':>10}")
        print("-" * 60)

        for d in self.dimensions:
            capacity, final_acc = self.estimate_capacity(d)

            # Bits = log2(capacity) for discrimination
            bits = np.log2(capacity) if capacity > 0 else 0
            bits_per_dim = bits / d

            results.append({
                "dimension": d,
                "capacity": capacity,
                "bits": bits,
                "bits_per_dim": bits_per_dim
            })

            print(f"{d:>10} | {capacity:>10} | {bits:>10.2f} | {bits_per_dim:>10.4f}")

        print()
        # Scaling analysis
        print("Scaling Analysis:")
        dims = [r["dimension"] for r in results]
        caps = [r["capacity"] for r in results]

        # Check if capacity scales with dimension
        if caps[-1] > caps[0]:
            ratio = caps[-1] / caps[0]
            dim_ratio = dims[-1] / dims[0]
            exponent = np.log(ratio) / np.log(dim_ratio)
            print(f"  Capacity scaling: d^{exponent:.2f}")
        else:
            print(f"  Capacity constant: ~{np.mean(caps):.1f} items")

        return results

if __name__ == "__main__":
    exp = CapacityEstimation()
    results = exp.run()

    output = {
        "cycle": 2041,
        "experiment": "Capacity Estimation",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2041_capacity_estimation.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
