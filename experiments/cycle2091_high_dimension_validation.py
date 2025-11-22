"""
Cycle 2091: High-Dimension Validation
=====================================
Validate the operational laws at D=4096.

Expected:
- N_operational = 0.0140 × 4096 = 57 items
- N_composition = 0.0105 × 4096 = 43 items
"""

import numpy as np
import json
import psutil
from datetime import datetime

class HighDimensionValidation:
    def __init__(self):
        self.dimension = 4096
        self.n_op = int(0.0140 * self.dimension)  # 57 items
        self.num_cycles = 200
        self.num_trials = 3  # Fewer trials due to longer runs
        self._entropy_counter = 0

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _get_entropy_vector(self, d):
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory().percent
        self._entropy_counter += 1
        seed = int((cpu * 1000 + mem * 10 + self._entropy_counter) * 1000) % (2**31)
        np.random.seed(seed)
        return np.random.normal(0, 0.01, d)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, seed):
        """Run with given number of items."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Run operation
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Test retrieval
        correct = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_experiment(self):
        """Test at different capacities."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_op_expected": self.n_op,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "capacities": []
        }

        print(f"D = {self.dimension}, expected N_op = {self.n_op}")
        print()
        print(f"{'Items':<10} {'% N_op':<12} {'Accuracy':<12}")
        print("-" * 35)

        # Test at 25%, 50%, 75%, 100% of predicted N_op
        for pct in [25, 50, 75, 100]:
            n_items = max(1, int(self.n_op * pct / 100))
            accuracies = []

            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, seed=trial*100+pct)
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            results["capacities"].append({
                "n_items": n_items,
                "pct_nop": pct,
                "accuracy": mean_acc
            })

            print(f"{n_items:<10} {pct}%{'':<9} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Validate the formula."""
        caps = results["capacities"]
        analysis = {"findings": []}

        # Check if 100% N_op achieves 80%
        at_100 = [c for c in caps if c["pct_nop"] == 100][0]

        if at_100["accuracy"] >= 0.8:
            analysis["findings"].append(
                f"Formula VALIDATED: {at_100['n_items']} items achieves {at_100['accuracy']*100:.0f}%"
            )
            analysis["validated"] = True
        else:
            # Find actual threshold
            for c in reversed(caps):
                if c["accuracy"] >= 0.8:
                    analysis["findings"].append(
                        f"Actual limit: {c['n_items']} items ({c['pct_nop']}% of predicted)"
                    )
                    break
            analysis["validated"] = False

        # Scaling check
        n_crit = int(0.042 * self.dimension)
        ratio = at_100["n_items"] / n_crit
        analysis["findings"].append(
            f"Operating at {ratio*100:.0f}% of theoretical N_crit"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2091: High-Dimension Validation (D=4096)")
    print("=" * 60)
    print()

    exp = HighDimensionValidation()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2091_high_dimension.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
