"""
Cycle 2080: Dimension Scaling Ratio
===================================
C2079 found operational capacity is 35% of N_crit at D=1024.

Question: Is this ratio universal across dimensions?
If yes, the deployment rule is: N_operational = 0.35 × 0.042 × D = 0.0147 × D

Test at D = 512, 1024, 2048
"""

import numpy as np
import json
import psutil
from datetime import datetime

class DimensionScalingRatio:
    def __init__(self):
        self.num_cycles_ratio = 10  # cycles = 10 × items
        self.num_trials = 5
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
        """V2 entropy with counter."""
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

    def run_trial(self, d, n_items, seed):
        """Run at given dimension and capacity."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        num_cycles = n_items * self.num_cycles_ratio

        # Create and store patterns
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

        # Run cycles
        for cycle in range(num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Final accuracy
        correct = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def find_operational_limit(self, d):
        """Binary search for 80% accuracy threshold."""
        n_crit = int(0.042 * d)

        # Test at different percentages of N_crit
        results = []
        for pct in [20, 30, 35, 40, 50]:
            n_items = max(1, int(n_crit * pct / 100))

            accuracies = []
            for trial in range(self.num_trials):
                acc = self.run_trial(d, n_items, seed=trial*100+pct+d)
                accuracies.append(acc)

            mean_acc = np.mean(accuracies)
            results.append({
                "pct_ncrit": pct,
                "n_items": n_items,
                "accuracy": float(mean_acc)
            })

        # Find threshold
        threshold = None
        for r in reversed(results):
            if r["accuracy"] >= 0.8:
                threshold = r
                break

        return results, threshold

    def run_experiment(self):
        """Test scaling across dimensions."""
        results = {
            "metadata": {
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "dimensions": []
        }

        print(f"{'Dimension':<12} {'N_crit':<10} {'Op Limit':<12} {'Ratio':<10}")
        print("-" * 50)

        for d in [512, 1024, 2048]:
            dimension_results, threshold = self.find_operational_limit(d)
            n_crit = int(0.042 * d)

            if threshold:
                ratio = threshold["pct_ncrit"] / 100
                op_items = threshold["n_items"]
            else:
                ratio = 0.20  # Lowest tested
                op_items = int(n_crit * 0.20)

            results["dimensions"].append({
                "dimension": d,
                "n_crit": n_crit,
                "operational_limit": op_items,
                "ratio": float(ratio),
                "details": dimension_results
            })

            print(f"{d:<12} {n_crit:<10} {op_items:<12} {ratio*100:.0f}%")

        return results

    def analyze(self, results):
        """Check if ratio is universal."""
        dims = results["dimensions"]
        analysis = {"findings": []}

        ratios = [d["ratio"] for d in dims]
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)

        if std_ratio < 0.05:
            analysis["findings"].append(
                f"Universal ratio confirmed: {mean_ratio*100:.0f}% (±{std_ratio*100:.0f}%)"
            )
            analysis["universal"] = True
        else:
            analysis["findings"].append(
                f"Ratio varies: {[f'{r*100:.0f}%' for r in ratios]}"
            )
            analysis["universal"] = False

        # Deployment formula
        coeff = mean_ratio * 0.042
        analysis["findings"].append(
            f"Deployment formula: N_op = {coeff:.4f} × D"
        )
        analysis["coefficient"] = float(coeff)

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2080: Dimension Scaling Ratio")
    print("=" * 60)
    print()

    exp = DimensionScalingRatio()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2080_dimension_ratio.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
