"""
Cycle 2093: Capacity Plateau Investigation
==========================================
C2092 found N_op ≈ 16 regardless of D (for D ≥ 512).
This is surprising - higher D should allow more capacity.

Hypotheses:
1. Noise accumulation over 200 cycles dominates
2. Cleanup codebook linear search becomes bottleneck
3. Fundamental binding interference limit

Test: Compare retrieval BEFORE and AFTER operation cycles.
If pre-operation is high but post-operation is low, noise is the issue.
"""

import numpy as np
import json
from datetime import datetime

class CapacityPlateauInvestigation:
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

    def run_trial(self, d, n_items, num_cycles, seed):
        """Run with configurable cycles and measure pre/post accuracy."""
        np.random.seed(seed)

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

        # Test BEFORE operation cycles
        correct_pre = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_pre += 1
        pre_acc = correct_pre / n_items

        # Run operation cycles
        for cycle in range(num_cycles):
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Test AFTER operation cycles
        correct_post = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_post += 1
        post_acc = correct_post / n_items

        return pre_acc, post_acc

    def run_experiment(self):
        """Test pre/post accuracy across dimensions and items."""
        results = {
            "metadata": {
                "num_trials": self.num_trials,
                "num_cycles": 200,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print("Testing pre-operation vs post-operation accuracy...")
        print()
        print(f"{'D':<8} {'Items':<8} {'Pre-Op':<10} {'Post-Op':<10} {'Δ':<10}")
        print("-" * 50)

        test_cases = [
            (512, 10),
            (512, 16),
            (512, 21),   # N_crit for D=512
            (1024, 10),
            (1024, 16),
            (1024, 32),
            (1024, 43),  # N_crit for D=1024
            (2048, 16),
            (2048, 32),
            (2048, 64),
        ]

        for d, n_items in test_cases:
            pre_accs = []
            post_accs = []

            for trial in range(self.num_trials):
                pre, post = self.run_trial(d, n_items, 200, seed=trial*100+d+n_items)
                pre_accs.append(pre)
                post_accs.append(post)

            mean_pre = np.mean(pre_accs)
            mean_post = np.mean(post_accs)
            delta = mean_post - mean_pre

            results["tests"].append({
                "d": d,
                "n_items": n_items,
                "pre_accuracy": float(mean_pre),
                "post_accuracy": float(mean_post),
                "delta": float(delta)
            })

            print(f"{d:<8} {n_items:<8} {mean_pre*100:>5.0f}%{'':<4} {mean_post*100:>5.0f}%{'':<4} {delta*100:>+5.0f}%")

        return results

    def analyze(self, results):
        """Determine cause of plateau."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check if pre-op accuracy is always high
        pre_accs = [t["pre_accuracy"] for t in tests]
        post_accs = [t["post_accuracy"] for t in tests]

        if min(pre_accs) > 0.9:
            analysis["findings"].append(
                "Pre-operation accuracy always high (>90%)"
            )
            analysis["pre_op_good"] = True
        else:
            # Find where pre-op fails
            failing = [t for t in tests if t["pre_accuracy"] < 0.8]
            if failing:
                analysis["findings"].append(
                    f"Pre-op fails at high items: {failing[0]['n_items']} items at D={failing[0]['d']}"
                )
            analysis["pre_op_good"] = False

        # Check degradation pattern
        avg_delta = np.mean([t["delta"] for t in tests])
        if avg_delta < -0.1:
            analysis["findings"].append(
                f"Operation cycles degrade accuracy by {abs(avg_delta)*100:.0f}% on average"
            )
            analysis["degradation"] = True
        else:
            analysis["degradation"] = False

        # Check if problem is worse at high D
        d_groups = {}
        for t in tests:
            d = t["d"]
            if d not in d_groups:
                d_groups[d] = []
            d_groups[d].append(t["delta"])

        for d in sorted(d_groups.keys()):
            avg = np.mean(d_groups[d])
            if abs(avg) > 0.05:
                analysis["findings"].append(
                    f"D={d}: avg degradation = {avg*100:+.0f}%"
                )

        # Diagnosis
        if analysis.get("pre_op_good") and analysis.get("degradation"):
            analysis["findings"].append(
                "DIAGNOSIS: Noise accumulation during operation causes plateau"
            )
        elif not analysis.get("pre_op_good"):
            analysis["findings"].append(
                "DIAGNOSIS: Binding interference at storage, not operation"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2093: Capacity Plateau Investigation")
    print("=" * 60)
    print()

    exp = CapacityPlateauInvestigation()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2093_capacity_plateau.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
