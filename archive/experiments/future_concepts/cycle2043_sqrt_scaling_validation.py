"""
Cycle 2043: Validate sqrt(d) Capacity Scaling
=============================================
Precise test of theoretical prediction: capacity ≈ k * sqrt(d)
"""

import numpy as np
import json
from datetime import datetime

class SqrtScalingValidation:
    def __init__(self):
        self.num_trials = 100
        self.dimensions = [256, 512, 1024, 2048, 4096]

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

    def find_capacity(self, d, target_acc=0.9):
        """Binary search for capacity at target accuracy."""
        low, high = 1, 200

        while high - low > 1:
            mid = (low + high) // 2
            acc = self.test_capacity(d, mid)
            if acc >= target_acc:
                low = mid
            else:
                high = mid

        return low

    def test_capacity(self, d, num_items):
        correct = 0

        for _ in range(self.num_trials):
            items = [self._generate(d) for _ in range(num_items)]
            np.random.seed(42)
            positions = [self._normalize(np.random.randn(d)) for _ in range(num_items)]
            np.random.seed(None)

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
        print("Cycle 2043: Validate sqrt(d) Capacity Scaling")
        print("-" * 60)

        results = []

        print(f"{'Dimension':>10} | {'sqrt(d)':>10} | {'Capacity':>10} | {'Cap/sqrt(d)':>12}")
        print("-" * 60)

        for d in self.dimensions:
            capacity = self.find_capacity(d)
            sqrt_d = np.sqrt(d)
            ratio = capacity / sqrt_d

            results.append({
                "dimension": d,
                "sqrt_d": sqrt_d,
                "capacity": capacity,
                "ratio": ratio
            })

            print(f"{d:>10} | {sqrt_d:>10.1f} | {capacity:>10} | {ratio:>12.2f}")

        print()
        # Compute scaling constant
        ratios = [r["ratio"] for r in results]
        k = np.mean(ratios)
        std = np.std(ratios)

        print(f"Scaling Law: capacity = {k:.2f} ± {std:.2f} * sqrt(d)")

        # R-squared for sqrt model
        dims = np.array([r["dimension"] for r in results])
        caps = np.array([r["capacity"] for r in results])
        predicted = k * np.sqrt(dims)
        ss_res = np.sum((caps - predicted) ** 2)
        ss_tot = np.sum((caps - np.mean(caps)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        print(f"R² = {r_squared:.4f}")

        return {
            "results": results,
            "scaling_constant": k,
            "scaling_std": std,
            "r_squared": r_squared
        }

if __name__ == "__main__":
    exp = SqrtScalingValidation()
    results = exp.run()

    output = {
        "cycle": 2043,
        "experiment": "Sqrt Scaling Validation",
        "timestamp": datetime.now().isoformat(),
        "scaling_law": f"capacity = {results['scaling_constant']:.2f} * sqrt(d)",
        "r_squared": results["r_squared"],
        "results": results["results"]
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2043_sqrt_scaling_validation.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
