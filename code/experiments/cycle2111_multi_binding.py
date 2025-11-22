"""
Cycle 2111: Multi-Binding Test
==============================
Can we store multiple values for the same key?

Method: Superimpose multiple bindings
memory = key ⊛ v1 + key ⊛ v2 + key ⊛ v3

Then query: key^(-1) ⊛ memory → superposition of values
Need cleanup against value codebook to retrieve each.
"""

import numpy as np
import json
from datetime import datetime

class MultiBindingTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _top_k_matches(self, noisy, codebook, k):
        """Return top k matches from codebook."""
        sims = [(np.dot(noisy, clean), clean) for clean in codebook]
        sims.sort(key=lambda x: -x[0])
        return [clean for sim, clean in sims[:k]]

    def run_trial(self, num_keys, values_per_key, seed):
        """Test multi-binding retrieval."""
        np.random.seed(seed)
        d = self.dimension

        memory = np.zeros(d)
        keys = []
        value_sets = []  # List of lists

        # Store multi-bindings
        for _ in range(num_keys):
            key = self._generate(d)
            values = [self._generate(d) for _ in range(values_per_key)]

            for value in values:
                binding = self._circ_conv(key, value)
                memory = self._normalize(memory + binding)

            keys.append(key)
            value_sets.append(values)

        # All values as codebook
        all_values = [v for vset in value_sets for v in vset]

        # Maintenance
        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.005, d)
            memory = self._normalize(memory + noise)

            # Refresh one binding
            key_idx = cycle % num_keys
            val_idx = cycle % values_per_key
            key = keys[key_idx]
            value = value_sets[key_idx][val_idx]
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + 0.3 * binding)

        # Test retrieval
        correct_any = 0  # At least one value correct
        correct_all = 0  # All values correct

        for key, values in zip(keys, value_sets):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)

            # Get top k matches
            matches = self._top_k_matches(retrieved, all_values, values_per_key)

            # Count how many correct
            found = 0
            for match in matches:
                for value in values:
                    if np.dot(match, value) > 0.9:  # High threshold for identity
                        found += 1
                        break

            if found >= 1:
                correct_any += 1
            if found == values_per_key:
                correct_all += 1

        any_acc = correct_any / num_keys
        all_acc = correct_all / num_keys

        return any_acc, all_acc

    def run_experiment(self):
        """Test multi-binding at various configurations."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}")
        print()
        print(f"{'Keys':<8} {'Vals/Key':<10} {'Total':<8} {'Any%':<10} {'All%':<10}")
        print("-" * 50)

        test_cases = [
            (5, 2),    # 10 bindings
            (5, 3),    # 15 bindings
            (3, 5),    # 15 bindings
            (4, 4),    # 16 bindings
        ]

        for num_keys, vals_per_key in test_cases:
            any_accs = []
            all_accs = []

            for trial in range(self.num_trials):
                any_acc, all_acc = self.run_trial(num_keys, vals_per_key, seed=trial*100+num_keys)
                any_accs.append(any_acc)
                all_accs.append(all_acc)

            mean_any = np.mean(any_accs)
            mean_all = np.mean(all_accs)
            total = num_keys * vals_per_key

            results["tests"].append({
                "num_keys": num_keys,
                "values_per_key": vals_per_key,
                "total_bindings": total,
                "any_correct": float(mean_any),
                "all_correct": float(mean_all)
            })

            print(f"{num_keys:<8} {vals_per_key:<10} {total:<8} {mean_any*100:>5.0f}%{'':<4} {mean_all*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate multi-binding capability."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check any-correct (at least one)
        avg_any = np.mean([t["any_correct"] for t in tests])
        avg_all = np.mean([t["all_correct"] for t in tests])

        if avg_any >= 0.8:
            analysis["findings"].append(
                f"Multi-binding retrieves at least one: {avg_any*100:.0f}%"
            )

        if avg_all >= 0.8:
            analysis["findings"].append(
                f"Multi-binding retrieves ALL values: {avg_all*100:.0f}%"
            )
        elif avg_all >= 0.5:
            analysis["findings"].append(
                f"Partial multi-binding: {avg_all*100:.0f}% get all values"
            )
        else:
            analysis["findings"].append(
                f"Multi-binding challenging: only {avg_all*100:.0f}% get all values"
            )

        # Best configuration
        best = max(tests, key=lambda x: x["all_correct"])
        analysis["findings"].append(
            f"Best: {best['num_keys']} keys × {best['values_per_key']} values"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2111: Multi-Binding Test")
    print("=" * 60)
    print()

    exp = MultiBindingTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2111_multi_binding.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
