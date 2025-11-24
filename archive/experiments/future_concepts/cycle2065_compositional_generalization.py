"""
Cycle 2065: Compositional Generalization
=========================================
Can the system compose learned parts into novel combinations?

From C2064: System learns features (98% transfer for similar patterns).
Question: Can it combine learned features compositionally?

Test: Train on A+B, A+C, B+C → Test retrieval of A+B+C
This is a hallmark of human cognition: productive composition.
"""

import numpy as np
import json
from datetime import datetime

class CompositionalGeneralization:
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

    def run_trial(self, seed):
        """Test compositional generalization."""
        np.random.seed(seed)
        d = self.dimension

        # Create atomic elements
        A = self._generate(d)
        B = self._generate(d)
        C = self._generate(d)

        # Create pairwise compositions
        AB = self._normalize(self._circ_conv(A, B))
        AC = self._normalize(self._circ_conv(A, C))
        BC = self._normalize(self._circ_conv(B, C))

        # Create novel triple composition (not trained)
        ABC = self._normalize(self._circ_conv(self._circ_conv(A, B), C))

        # Store training patterns
        memory = np.zeros(d)

        # Add pairwise bindings with unique keys
        key_AB = self._generate(d)
        key_AC = self._generate(d)
        key_BC = self._generate(d)

        memory = self._normalize(memory + self._circ_conv(key_AB, AB))
        memory = self._normalize(memory + self._circ_conv(key_AC, AC))
        memory = self._normalize(memory + self._circ_conv(key_BC, BC))

        # Also store atoms for reference
        key_A = self._generate(d)
        key_B = self._generate(d)
        key_C = self._generate(d)

        memory = self._normalize(memory + self._circ_conv(key_A, A))
        memory = self._normalize(memory + self._circ_conv(key_B, B))
        memory = self._normalize(memory + self._circ_conv(key_C, C))

        # Create key for novel composition
        key_ABC = self._generate(d)

        # Measure initial retrieval ability
        def get_similarity(key, value):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            return np.dot(retrieved, value)

        initial_AB = get_similarity(key_AB, AB)
        initial_AC = get_similarity(key_AC, AC)
        initial_BC = get_similarity(key_BC, BC)

        # Can we retrieve ABC without training?
        # Strategy: Compose retrievals of parts
        retrieved_A = self._circ_conv(memory, np.roll(key_A[::-1], 1))
        retrieved_B = self._circ_conv(memory, np.roll(key_B[::-1], 1))
        retrieved_C = self._circ_conv(memory, np.roll(key_C[::-1], 1))

        # Compose retrieved atoms
        composed_ABC = self._normalize(
            self._circ_conv(self._circ_conv(retrieved_A, retrieved_B), retrieved_C)
        )
        initial_composition = np.dot(composed_ABC, ABC)

        # Run Hebbian strengthening on training patterns
        phi = (1 + np.sqrt(5)) / 2
        comp_prob = 0.1 * phi
        decomp_prob = 0.1 / phi

        train_keys = [key_AB, key_AC, key_BC, key_A, key_B, key_C]
        train_values = [AB, AC, BC, A, B, C]
        refresh_idx = 0

        for cycle in range(self.num_cycles):
            # Perturbation
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            # Composition
            if np.random.random() < comp_prob:
                new_key = self._generate(d)
                new_value = self._generate(d)
                binding = self._circ_conv(new_key, new_value)
                memory = self._normalize(memory + 0.1 * binding)

            # Decomposition
            if np.random.random() < decomp_prob:
                memory = self._normalize(memory + np.random.normal(0, 0.05, d))

            # Refresh training patterns
            binding = self._circ_conv(train_keys[refresh_idx], train_values[refresh_idx])
            memory = self._normalize(memory + 0.5 * binding)
            refresh_idx = (refresh_idx + 1) % len(train_keys)

        # Measure final retrieval
        final_AB = get_similarity(key_AB, AB)
        final_AC = get_similarity(key_AC, AC)
        final_BC = get_similarity(key_BC, BC)

        # Try compositional retrieval again
        retrieved_A = self._circ_conv(memory, np.roll(key_A[::-1], 1))
        retrieved_B = self._circ_conv(memory, np.roll(key_B[::-1], 1))
        retrieved_C = self._circ_conv(memory, np.roll(key_C[::-1], 1))

        composed_ABC = self._normalize(
            self._circ_conv(self._circ_conv(retrieved_A, retrieved_B), retrieved_C)
        )
        final_composition = np.dot(composed_ABC, ABC)

        return {
            "initial_pairwise": np.mean([initial_AB, initial_AC, initial_BC]),
            "final_pairwise": np.mean([final_AB, final_AC, final_BC]),
            "pairwise_change": np.mean([final_AB, final_AC, final_BC]) - np.mean([initial_AB, initial_AC, initial_BC]),
            "initial_composition": initial_composition,
            "final_composition": final_composition,
            "composition_change": final_composition - initial_composition,
            "composition_success": final_composition > 0.1
        }

    def run_experiment(self):
        """Run multiple trials."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "trials": []
        }

        trial_results = []
        for trial in range(self.num_trials):
            result = self.run_trial(seed=trial*100)
            trial_results.append(result)

        # Aggregate
        mean_pairwise_change = np.mean([r["pairwise_change"] for r in trial_results])
        mean_composition_change = np.mean([r["composition_change"] for r in trial_results])
        composition_success_rate = np.mean([r["composition_success"] for r in trial_results])
        mean_initial_comp = np.mean([r["initial_composition"] for r in trial_results])
        mean_final_comp = np.mean([r["final_composition"] for r in trial_results])

        results["summary"] = {
            "mean_pairwise_change": float(mean_pairwise_change),
            "mean_composition_change": float(mean_composition_change),
            "composition_success_rate": float(composition_success_rate),
            "mean_initial_composition": float(mean_initial_comp),
            "mean_final_composition": float(mean_final_comp)
        }

        print(f"Pairwise Δ: {mean_pairwise_change*100:+.1f}%")
        print(f"Composition Δ: {mean_composition_change*100:+.1f}%")
        print(f"Initial composition similarity: {mean_initial_comp:.3f}")
        print(f"Final composition similarity: {mean_final_comp:.3f}")
        print(f"Composition success rate: {composition_success_rate*100:.0f}%")

        return results

    def analyze(self, results):
        """Determine if compositional generalization occurs."""
        summary = results["summary"]

        analysis = {
            "findings": [],
            "compositionality": "UNKNOWN"
        }

        if summary["mean_composition_change"] > 0.05:
            analysis["compositionality"] = "CONFIRMED"
            analysis["findings"].append(
                f"Composition improved by {summary['mean_composition_change']*100:.1f}% without direct training"
            )
        else:
            analysis["compositionality"] = "LIMITED"
            analysis["findings"].append(
                f"Composition change: {summary['mean_composition_change']*100:.1f}% (below threshold)"
            )

        if summary["composition_success_rate"] > 0.5:
            analysis["findings"].append(
                f"Composition succeeds in {summary['composition_success_rate']*100:.0f}% of trials"
            )
        else:
            analysis["findings"].append(
                f"Composition often fails ({summary['composition_success_rate']*100:.0f}% success)"
            )

        # Compare to pairwise
        ratio = summary["mean_final_composition"] / (summary["mean_pairwise_change"] + 0.5)
        analysis["findings"].append(
            f"Composition/Pairwise ratio: {ratio:.2f}"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2065: Compositional Generalization")
    print("=" * 60)
    print()

    exp = CompositionalGeneralization()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Compositionality: {analysis['compositionality']}")
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2065_compositional.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
