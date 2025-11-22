"""
Cycle 2004: Dimensionality Scaling of Working Memory
====================================================
C2003 found working memory limit of ~3 steps at d=2048.

Question: How does working memory scale with dimension?

Hypothesis: Higher dimensions provide more "room" for independent
bindings, extending working memory depth.

Method: Test chain depth 3 at dimensions 512, 1024, 2048, 4096.
"""

import numpy as np
import json
from datetime import datetime

class DimensionScaling:
    def __init__(self):
        self.dimensions = [512, 1024, 2048, 4096]
        self.test_depth = 3
        self.num_trials = 50

    def test_dimension(self, d):
        correct = 0
        total_sim = 0.0

        for _ in range(self.num_trials):
            # Generate concepts
            concepts = []
            for _ in range(self.test_depth + 1):
                v = np.random.normal(0, 1.0/np.sqrt(d), d)
                v = v / np.linalg.norm(v)
                concepts.append(v)

            # Create rules
            rules = []
            for i in range(self.test_depth):
                rule = np.real(np.fft.ifft(
                    np.fft.fft(concepts[i]) * np.fft.fft(concepts[i+1])))
                rules.append(rule)

            # Chain inference
            current = concepts[0]
            for i in range(self.test_depth):
                next_approx = np.real(np.fft.ifft(
                    np.fft.fft(rules[i]) * np.conj(np.fft.fft(current))))
                current = next_approx

            # Compare
            norm = np.linalg.norm(current)
            if norm > 0:
                current = current / norm
            target = concepts[self.test_depth]
            sim = np.dot(current, target)
            total_sim += sim

            if sim > 0.3:
                correct += 1

        return {
            "accuracy": correct / self.num_trials,
            "avg_sim": total_sim / self.num_trials
        }

    def run(self):
        print("Cycle 2004: Dimensionality Scaling")
        print("-" * 50)
        print(f"Testing {self.test_depth}-step chains at various dimensions")
        print()

        results = []

        print(f"{'Dimension':>10} | {'Accuracy':>10} | {'Similarity':>10}")
        print("-" * 40)

        for d in self.dimensions:
            r = self.test_dimension(d)
            results.append({
                "dimension": d,
                "accuracy": r["accuracy"],
                "similarity": r["avg_sim"]
            })
            print(f"{d:>10} | {r['accuracy']*100:>9.1f}% | {r['avg_sim']:>10.4f}")

        print()
        self._analyze(results)
        return results

    def _analyze(self, results):
        print("-" * 50)
        print("SCALING ANALYSIS")
        print("-" * 50)

        # Check scaling
        sims = [r["similarity"] for r in results]
        dims = [r["dimension"] for r in results]

        # Log-log scaling
        if len(dims) >= 2:
            log_dims = np.log(dims)
            log_sims = np.log(np.array(sims) + 0.1)  # Offset for stability

            # Simple linear regression
            slope = (log_sims[-1] - log_sims[0]) / (log_dims[-1] - log_dims[0])
            print(f"\nScaling exponent: {slope:.3f}")
            print("  (sim ~ d^α)")

        # Projection
        if results[-1]["accuracy"] > 0.9:
            print("\n4096 achieves >90% accuracy at depth 3")
            print("Higher dimensions may support deeper chains")
        else:
            print(f"\nEven d=4096 only achieves {results[-1]['accuracy']*100:.0f}%")
            print("Dimensionality alone doesn't solve working memory limit")

if __name__ == "__main__":
    exp = DimensionScaling()
    results = exp.run()

    output = {
        "cycle": 2004,
        "experiment": "Dimension Scaling",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Higher dimensions extend working memory",
        "test_depth": 3,
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2004_dimension_scaling.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
