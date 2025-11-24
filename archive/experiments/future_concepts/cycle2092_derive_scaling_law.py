"""
Cycle 2092: Derive True Scaling Law
===================================
C2080 and C2091 showed the ratio decreases with D:
- D=512:  ~50% of N_crit
- D=1024: ~30% of N_crit
- D=2048: ~20% of N_crit
- D=4096: <15% of N_crit

This suggests: N_op ∝ D^α where α < 1

Test hypothesis: N_op = c × D^0.5 (square root scaling)
"""

import numpy as np
import json
from datetime import datetime

class DeriveScalingLaw:
    def __init__(self):
        self.num_trials = 3
        self._entropy_counter = 0

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

    def run_trial(self, d, n_items, seed):
        """Run standard operation."""
        np.random.seed(seed)
        num_cycles = 200

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
        for cycle in range(num_cycles):
            noise = np.random.normal(0, 0.01, d)
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

    def find_operational_limit(self, d):
        """Binary search for 80% accuracy threshold."""
        low, high = 1, int(0.042 * d)  # Between 1 and N_crit
        best = 1

        for _ in range(8):  # 8 iterations for precision
            mid = (low + high) // 2
            if mid == 0:
                break

            accs = []
            for trial in range(self.num_trials):
                acc = self.run_trial(d, mid, seed=trial*100+d+mid)
                accs.append(acc)

            mean_acc = np.mean(accs)

            if mean_acc >= 0.8:
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        return best

    def run_experiment(self):
        """Test multiple dimensions and fit scaling law."""
        results = {
            "metadata": {
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "dimensions": []
        }

        print("Finding operational limits at each dimension...")
        print()
        print(f"{'D':<10} {'N_op':<10} {'N_crit':<10} {'Ratio':<10} {'√D':<10}")
        print("-" * 55)

        dimensions = [256, 512, 1024, 2048]

        for d in dimensions:
            n_op = self.find_operational_limit(d)
            n_crit = int(0.042 * d)
            ratio = n_op / n_crit
            sqrt_d = np.sqrt(d)

            results["dimensions"].append({
                "d": d,
                "n_op": n_op,
                "n_crit": n_crit,
                "ratio": float(ratio),
                "sqrt_d": float(sqrt_d)
            })

            print(f"{d:<10} {n_op:<10} {n_crit:<10} {ratio:.2f}{'':<8} {sqrt_d:.0f}")

        return results

    def analyze(self, results):
        """Fit and validate scaling law."""
        dims = results["dimensions"]
        analysis = {"findings": []}

        # Fit N_op = c × D^α
        D = np.array([d["d"] for d in dims])
        N = np.array([d["n_op"] for d in dims])

        # Log-log fit: log(N) = log(c) + α×log(D)
        log_D = np.log(D)
        log_N = np.log(N)

        # Linear regression
        alpha = np.sum((log_D - np.mean(log_D)) * (log_N - np.mean(log_N))) / \
                np.sum((log_D - np.mean(log_D))**2)
        log_c = np.mean(log_N) - alpha * np.mean(log_D)
        c = np.exp(log_c)

        analysis["findings"].append(
            f"Scaling law: N_op = {c:.3f} × D^{alpha:.2f}"
        )
        analysis["coefficient"] = float(c)
        analysis["exponent"] = float(alpha)

        # Test fit quality
        predicted = c * D**alpha
        errors = np.abs(N - predicted) / N * 100
        max_error = np.max(errors)

        if max_error < 30:
            analysis["findings"].append(f"Good fit: max error {max_error:.0f}%")
        else:
            analysis["findings"].append(f"Moderate fit: max error {max_error:.0f}%")

        # Compare to square root
        sqrt_coeff = np.mean(N / np.sqrt(D))
        sqrt_pred = sqrt_coeff * np.sqrt(D)
        sqrt_errors = np.abs(N - sqrt_pred) / N * 100

        if np.mean(sqrt_errors) < np.mean(errors):
            analysis["findings"].append(
                f"Square root model better: N_op ≈ {sqrt_coeff:.2f}√D"
            )
            analysis["sqrt_coefficient"] = float(sqrt_coeff)

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2092: Derive True Scaling Law")
    print("=" * 60)
    print()

    exp = DeriveScalingLaw()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2092_scaling_law.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
