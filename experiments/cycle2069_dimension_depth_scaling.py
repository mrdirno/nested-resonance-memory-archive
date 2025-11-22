"""
Cycle 2069: Dimension-Depth Scaling
====================================
Can higher dimension buy deeper recursion?

From C2068: Cleanup extends depth from 2 to 8.
Question: Does D=2048 or D=4096 allow even deeper?
"""

import numpy as np
import json
from datetime import datetime

class DimensionDepthScaling:
    def __init__(self):
        self.dimensions = [512, 1024, 2048, 4096]
        self.max_depth = 10
        self.num_trials = 5

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def find_max_depth(self, dimension, seed):
        """Find max depth for given dimension."""
        np.random.seed(seed)
        d = dimension

        for depth in range(1, self.max_depth + 1):
            # Create atoms
            atoms = [self._generate(d) for _ in range(depth + 1)]
            codebook = atoms.copy()

            # Build target composition
            composed = atoms[0]
            for i in range(1, depth + 1):
                composed = self._normalize(self._circ_conv(composed, atoms[i]))

            # Store and retrieve
            memory = np.zeros(d)
            keys = []
            for atom in atoms:
                key = self._generate(d)
                memory = self._normalize(memory + self._circ_conv(key, atom))
                keys.append(key)

            # Retrieve with cleanup
            retrieved_composed = None
            for i, key in enumerate(keys):
                key_inv = np.roll(key[::-1], 1)
                retrieved = self._circ_conv(memory, key_inv)
                retrieved = self._cleanup(retrieved, codebook)

                if retrieved_composed is None:
                    retrieved_composed = retrieved
                else:
                    retrieved_composed = self._normalize(
                        self._circ_conv(retrieved_composed, retrieved)
                    )

            # Check success
            similarity = np.dot(retrieved_composed, composed)
            if similarity <= 0.1:
                return depth - 1  # Previous depth was max

        return self.max_depth

    def run_experiment(self):
        """Test dimension-depth relationship."""
        results = {
            "metadata": {
                "dimensions": self.dimensions,
                "max_depth": self.max_depth,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Dimension':<12} {'Max Depth':<12} {'Depth/√D':<12}")
        print("-" * 40)

        for dim in self.dimensions:
            depths = []
            for trial in range(self.num_trials):
                max_depth = self.find_max_depth(dim, seed=trial*100 + dim)
                depths.append(max_depth)

            mean_depth = np.mean(depths)
            ratio = mean_depth / np.sqrt(dim)

            condition = {
                "dimension": dim,
                "mean_max_depth": float(mean_depth),
                "depth_per_sqrt_d": float(ratio)
            }
            results["conditions"].append(condition)

            print(f"{dim:<12} {mean_depth:<12.1f} {ratio:<12.4f}")

        return results

    def analyze(self, results):
        """Check if depth scales with dimension."""
        conditions = results["conditions"]

        dims = [c["dimension"] for c in conditions]
        depths = [c["mean_max_depth"] for c in conditions]

        # Check sqrt scaling
        sqrt_dims = [np.sqrt(d) for d in dims]
        coeffs = np.polyfit(sqrt_dims, depths, 1)
        predicted = np.polyval(coeffs, sqrt_dims)
        r_squared = 1 - np.sum((np.array(depths) - predicted)**2) / np.sum((np.array(depths) - np.mean(depths))**2)

        analysis = {
            "scaling_type": "SQRT" if r_squared > 0.9 else "OTHER",
            "r_squared": float(r_squared),
            "slope": float(coeffs[0]),
            "findings": []
        }

        if r_squared > 0.9:
            analysis["findings"].append(
                f"Depth scales with √D (R²={r_squared:.3f})"
            )
            analysis["findings"].append(
                f"Depth ≈ {coeffs[0]:.2f} × √D + {coeffs[1]:.1f}"
            )
        else:
            analysis["findings"].append(
                f"Scaling unclear (R²={r_squared:.3f})"
            )

        # Practical implications
        max_cond = max(conditions, key=lambda x: x["mean_max_depth"])
        analysis["findings"].append(
            f"Best: D={max_cond['dimension']} achieves depth {max_cond['mean_max_depth']:.0f}"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2069: Dimension-Depth Scaling")
    print("=" * 60)
    print()

    exp = DimensionDepthScaling()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2069_dimension_depth.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
