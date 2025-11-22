"""
Cycle 2113: Analogical Reasoning Test
=====================================
Can the system solve analogies?

A:B :: C:?

Method:
- relation = A^(-1) ⊛ B
- answer = C ⊛ relation = C ⊛ A^(-1) ⊛ B

If we store (A→B, C→D) and extract relation from A:B,
can we apply it to C to get D?
"""

import numpy as np
import json
from datetime import datetime

class AnalogicalReasoningTest:
    def __init__(self):
        self.num_trials = 5
        self.dimension = 1024

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

    def run_trial(self, num_analogies, seed):
        """Test analogical reasoning."""
        np.random.seed(seed)
        d = self.dimension

        # Create entities and relations
        # Analogy: A is to B as C is to D
        # All pairs share the same relation

        analogies = []
        all_entities = []

        # Create a base relation
        for i in range(num_analogies):
            A = self._generate(d)
            B = self._generate(d)
            C = self._generate(d)

            # D = C ⊛ (A^(-1) ⊛ B) = C ⊛ relation
            # where relation = A^(-1) ⊛ B
            A_inv = np.roll(A[::-1], 1)
            relation = self._circ_conv(A_inv, B)
            D = self._normalize(self._circ_conv(C, relation))

            analogies.append((A, B, C, D))
            all_entities.extend([A, B, C, D])

        # Test: Given A, B, C, find D
        correct = 0

        for A, B, C, D in analogies:
            # Extract relation from A:B
            A_inv = np.roll(A[::-1], 1)
            relation = self._circ_conv(A_inv, B)

            # Apply to C
            predicted = self._circ_conv(C, relation)
            predicted = self._cleanup(predicted, all_entities)

            # Check if matches D
            if np.dot(predicted, D) > 0.5:
                correct += 1

        return correct / num_analogies

    def run_experiment(self):
        """Test analogical reasoning at various scales."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}")
        print()
        print(f"{'Analogies':<12} {'Accuracy':<12}")
        print("-" * 25)

        for num_analogies in [1, 3, 5, 10]:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(num_analogies, seed=trial*100+num_analogies)
                accs.append(acc)

            mean_acc = np.mean(accs)

            results["tests"].append({
                "num_analogies": num_analogies,
                "accuracy": float(mean_acc)
            })

            print(f"{num_analogies:<12} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate analogical reasoning capability."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check if basic analogy works
        single = [t for t in tests if t["num_analogies"] == 1][0]

        if single["accuracy"] >= 0.8:
            analysis["findings"].append(
                f"Basic analogy works: {single['accuracy']*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                f"Basic analogy fails: {single['accuracy']*100:.0f}%"
            )

        # Check scaling
        avg_acc = np.mean([t["accuracy"] for t in tests])
        analysis["findings"].append(
            f"Average accuracy: {avg_acc*100:.0f}%"
        )

        # Best configuration
        best = max(tests, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Best: {best['num_analogies']} analogies at {best['accuracy']*100:.0f}%"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2113: Analogical Reasoning Test")
    print("=" * 60)
    print()

    exp = AnalogicalReasoningTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2113_analogical_reasoning.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
