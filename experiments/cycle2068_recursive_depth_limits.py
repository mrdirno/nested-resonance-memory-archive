"""
Cycle 2068: Recursive Depth Limits
===================================
How deep can compositions go before cleanup fails?

Depth 1: A+B
Depth 2: (A+B)+C
Depth 3: ((A+B)+C)+D
...

This maps the fundamental limits of hierarchical cognition.
"""

import numpy as np
import json
from datetime import datetime

class RecursiveDepthLimits:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 10
        self.max_depth = 8

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup(self, noisy, codebook):
        """Auto-associative cleanup."""
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, depth, use_cleanup, seed):
        """Test composition at given depth."""
        np.random.seed(seed)
        d = self.dimension

        # Create atoms
        atoms = [self._generate(d) for _ in range(depth + 1)]
        codebook = atoms.copy()

        # Build composition recursively
        # Depth 1: atoms[0] * atoms[1]
        # Depth 2: (atoms[0] * atoms[1]) * atoms[2]
        # etc.

        composed = atoms[0]
        for i in range(1, depth + 1):
            composed = self._normalize(self._circ_conv(composed, atoms[i]))

        # Store in memory and retrieve
        memory = np.zeros(d)
        keys = []

        # Store atoms
        for atom in atoms:
            key = self._generate(d)
            memory = self._normalize(memory + self._circ_conv(key, atom))
            keys.append(key)

        # Retrieve and compose
        retrieved_composed = None
        for i, key in enumerate(keys):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)

            if use_cleanup:
                retrieved = self._cleanup(retrieved, codebook)

            if retrieved_composed is None:
                retrieved_composed = retrieved
            else:
                retrieved_composed = self._normalize(
                    self._circ_conv(retrieved_composed, retrieved)
                )

        # Measure similarity to target
        similarity = np.dot(retrieved_composed, composed)
        success = similarity > 0.1

        return {
            "depth": depth,
            "use_cleanup": use_cleanup,
            "similarity": similarity,
            "success": success
        }

    def run_experiment(self):
        """Test across depths with and without cleanup."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_trials": self.num_trials,
                "max_depth": self.max_depth,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        print(f"{'Depth':<8} {'No Cleanup':<15} {'With Cleanup':<15}")
        print("-" * 40)

        for depth in range(1, self.max_depth + 1):
            for use_cleanup in [False, True]:
                trial_results = []
                for trial in range(self.num_trials):
                    result = self.run_trial(depth, use_cleanup, seed=trial*100 + depth)
                    trial_results.append(result)

                mean_sim = np.mean([r["similarity"] for r in trial_results])
                success_rate = np.mean([r["success"] for r in trial_results])

                condition = {
                    "depth": depth,
                    "use_cleanup": use_cleanup,
                    "mean_similarity": float(mean_sim),
                    "success_rate": float(success_rate)
                }
                results["conditions"].append(condition)

            # Print row
            no_clean = [c for c in results["conditions"]
                       if c["depth"] == depth and not c["use_cleanup"]][0]
            with_clean = [c for c in results["conditions"]
                         if c["depth"] == depth and c["use_cleanup"]][0]

            print(f"{depth:<8} {no_clean['success_rate']*100:<15.0f}% {with_clean['success_rate']*100:<15.0f}%")

        return results

    def analyze(self, results):
        """Find depth limits."""
        conditions = results["conditions"]

        # Find max depth with >50% success
        no_cleanup_limit = 0
        cleanup_limit = 0

        for depth in range(1, self.max_depth + 1):
            no_clean = [c for c in conditions
                       if c["depth"] == depth and not c["use_cleanup"]][0]
            with_clean = [c for c in conditions
                         if c["depth"] == depth and c["use_cleanup"]][0]

            if no_clean["success_rate"] >= 0.5:
                no_cleanup_limit = depth
            if with_clean["success_rate"] >= 0.5:
                cleanup_limit = depth

        analysis = {
            "no_cleanup_limit": no_cleanup_limit,
            "cleanup_limit": cleanup_limit,
            "depth_gain": cleanup_limit - no_cleanup_limit,
            "findings": []
        }

        analysis["findings"].append(
            f"Without cleanup: Max depth = {no_cleanup_limit}"
        )
        analysis["findings"].append(
            f"With cleanup: Max depth = {cleanup_limit}"
        )
        analysis["findings"].append(
            f"Cleanup extends depth by {cleanup_limit - no_cleanup_limit} levels"
        )

        # Check for sharp transition
        for use_cleanup in [False, True]:
            conds = sorted([c for c in conditions if c["use_cleanup"] == use_cleanup],
                          key=lambda x: x["depth"])
            rates = [c["success_rate"] for c in conds]
            if len(rates) > 1:
                drops = [rates[i] - rates[i+1] for i in range(len(rates)-1)]
                max_drop = max(drops)
                drop_idx = drops.index(max_drop) + 1
                if max_drop > 0.3:
                    label = "with" if use_cleanup else "without"
                    analysis["findings"].append(
                        f"Sharp cliff {label} cleanup at depth {drop_idx+1}"
                    )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2068: Recursive Depth Limits")
    print("=" * 60)
    print()

    exp = RecursiveDepthLimits()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2068_depth_limits.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
