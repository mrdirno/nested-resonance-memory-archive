"""
Cycle 2066: Auto-Associative Cleanup for Composition
=====================================================
Can cleanup operations fix compositional generalization?

From C2065: Composition fails (30%) due to compounding noise.
Hypothesis: Auto-associative cleanup can denoise intermediate results.

Method: After each retrieval, pass through cleanup network before composing.
"""

import numpy as np
import json
from datetime import datetime

class CleanupComposition:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 300
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup(self, noisy, codebook):
        """Find closest vector in codebook (auto-associative cleanup)."""
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, use_cleanup, seed):
        """Test composition with or without cleanup."""
        np.random.seed(seed)
        d = self.dimension

        # Create atomic elements
        A = self._generate(d)
        B = self._generate(d)
        C = self._generate(d)

        # Codebook for cleanup
        codebook = [A, B, C]

        # Create compositions
        AB = self._normalize(self._circ_conv(A, B))
        AC = self._normalize(self._circ_conv(A, C))
        BC = self._normalize(self._circ_conv(B, C))
        ABC = self._normalize(self._circ_conv(self._circ_conv(A, B), C))

        # Store patterns
        memory = np.zeros(d)

        key_AB = self._generate(d)
        key_AC = self._generate(d)
        key_BC = self._generate(d)
        key_A = self._generate(d)
        key_B = self._generate(d)
        key_C = self._generate(d)

        memory = self._normalize(memory + self._circ_conv(key_AB, AB))
        memory = self._normalize(memory + self._circ_conv(key_AC, AC))
        memory = self._normalize(memory + self._circ_conv(key_BC, BC))
        memory = self._normalize(memory + self._circ_conv(key_A, A))
        memory = self._normalize(memory + self._circ_conv(key_B, B))
        memory = self._normalize(memory + self._circ_conv(key_C, C))

        # Run Hebbian strengthening
        phi = (1 + np.sqrt(5)) / 2
        comp_prob = 0.1 * phi
        decomp_prob = 0.1 / phi

        train_keys = [key_AB, key_AC, key_BC, key_A, key_B, key_C]
        train_values = [AB, AC, BC, A, B, C]
        refresh_idx = 0

        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            binding = self._circ_conv(train_keys[refresh_idx], train_values[refresh_idx])
            memory = self._normalize(memory + 0.5 * binding)
            refresh_idx = (refresh_idx + 1) % len(train_keys)

        # Retrieve and compose
        retrieved_A = self._circ_conv(memory, np.roll(key_A[::-1], 1))
        retrieved_B = self._circ_conv(memory, np.roll(key_B[::-1], 1))
        retrieved_C = self._circ_conv(memory, np.roll(key_C[::-1], 1))

        if use_cleanup:
            # Clean up retrieved atoms before composition
            retrieved_A = self._cleanup(retrieved_A, codebook)
            retrieved_B = self._cleanup(retrieved_B, codebook)
            retrieved_C = self._cleanup(retrieved_C, codebook)

        # Compose
        composed_ABC = self._normalize(
            self._circ_conv(self._circ_conv(retrieved_A, retrieved_B), retrieved_C)
        )

        similarity = np.dot(composed_ABC, ABC)
        success = similarity > 0.1

        return {
            "use_cleanup": use_cleanup,
            "similarity": similarity,
            "success": success
        }

    def run_experiment(self):
        """Compare with and without cleanup."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "conditions": []
        }

        for use_cleanup in [False, True]:
            trial_results = []
            for trial in range(self.num_trials):
                result = self.run_trial(use_cleanup, seed=trial*100)
                trial_results.append(result)

            mean_sim = np.mean([r["similarity"] for r in trial_results])
            success_rate = np.mean([r["success"] for r in trial_results])

            condition = {
                "cleanup": use_cleanup,
                "mean_similarity": float(mean_sim),
                "success_rate": float(success_rate)
            }
            results["conditions"].append(condition)

            label = "With Cleanup" if use_cleanup else "No Cleanup"
            print(f"{label}: Similarity={mean_sim:.3f}, Success={success_rate*100:.0f}%")

        return results

    def analyze(self, results):
        """Determine if cleanup helps."""
        no_cleanup = [c for c in results["conditions"] if not c["cleanup"]][0]
        with_cleanup = [c for c in results["conditions"] if c["cleanup"]][0]

        improvement = with_cleanup["success_rate"] - no_cleanup["success_rate"]

        analysis = {
            "no_cleanup_success": no_cleanup["success_rate"],
            "with_cleanup_success": with_cleanup["success_rate"],
            "improvement": improvement,
            "findings": []
        }

        if improvement > 0.2:
            analysis["status"] = "CLEANUP_EFFECTIVE"
            analysis["findings"].append(
                f"Cleanup improves composition by {improvement*100:.0f}% ({no_cleanup['success_rate']*100:.0f}% → {with_cleanup['success_rate']*100:.0f}%)"
            )
        elif improvement > 0:
            analysis["status"] = "PARTIAL_IMPROVEMENT"
            analysis["findings"].append(
                f"Marginal improvement: {improvement*100:.0f}%"
            )
        else:
            analysis["status"] = "NO_IMPROVEMENT"
            analysis["findings"].append("Cleanup does not help composition")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2066: Auto-Associative Cleanup for Composition")
    print("=" * 60)
    print()

    exp = CleanupComposition()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Status: {analysis['status']}")
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2066_cleanup_composition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
