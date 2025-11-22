"""
Cycle 2075: Capacity Scaling with True Entropy
==============================================
Test how the system scales with number of items using V2 entropy.

Question: Does the fixed entropy method maintain performance
as we approach and exceed N_crit?

From C2063: N_crit ≈ 0.042 × D = 43 items for D=1024
"""

import numpy as np
import json
import psutil
from datetime import datetime

class CapacityScalingTrueEntropy:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 100
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
        """V2 entropy with counter for uniqueness."""
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

    def run_trial(self, n_items, entropy_type, seed):
        """Run with given number of items."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

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

        # Run cycles with entropy and Hebbian refresh
        for cycle in range(self.num_cycles):
            # Add noise
            if entropy_type == "synthetic":
                noise = np.random.normal(0, 0.01, d)
            elif entropy_type == "real":
                noise = self._get_entropy_vector(d)
            else:
                noise = np.zeros(d)

            memory = self._normalize(memory + noise)

            # Hebbian refresh (round-robin)
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

    def run_experiment(self):
        """Test scaling across item counts."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "n_crit": int(0.042 * self.dimension),
                "timestamp": datetime.now().isoformat()
            },
            "scaling": []
        }

        # N_crit ≈ 43 for D=1024
        n_crit = int(0.042 * self.dimension)

        print(f"N_crit = {n_crit} (0.042 × {self.dimension})")
        print()
        print(f"{'Items':<10} {'% N_crit':<12} {'None':<10} {'Synthetic':<12} {'Real V2':<10}")
        print("-" * 60)

        # Test 25%, 50%, 75%, 100%, 125%, 150% of N_crit
        for pct in [25, 50, 75, 100, 125, 150]:
            n_items = max(1, int(n_crit * pct / 100))
            row = {"n_items": n_items, "pct_ncrit": pct}

            for entropy_type in ["none", "synthetic", "real"]:
                accuracies = []
                for trial in range(self.num_trials):
                    acc = self.run_trial(n_items, entropy_type, seed=trial*100+pct)
                    accuracies.append(acc)
                row[entropy_type] = float(np.mean(accuracies))

            results["scaling"].append(row)

            print(f"{n_items:<10} {pct}%{'':<9} {row['none']*100:<10.0f}% {row['synthetic']*100:<12.0f}% {row['real']*100:<10.0f}%")

        return results

    def analyze(self, results):
        """Analyze scaling behavior."""
        scaling = results["scaling"]
        analysis = {"findings": []}

        # Check if real matches synthetic at each scale
        all_match = True
        for row in scaling:
            diff = abs(row["real"] - row["synthetic"])
            if diff > 0.15:
                all_match = False
                analysis["findings"].append(
                    f"Gap at {row['pct_ncrit']}%: Real {row['real']*100:.0f}% vs Synth {row['synthetic']*100:.0f}%"
                )

        if all_match:
            analysis["findings"].append("V2 entropy scales with synthetic across all capacities")

        # Check capacity threshold
        for row in scaling:
            if row["real"] < 0.8 and row["pct_ncrit"] <= 100:
                analysis["findings"].append(
                    f"Capacity concern: {row['real']*100:.0f}% at {row['pct_ncrit']}% N_crit"
                )
                break

        # Check degradation beyond N_crit
        at_100 = [r for r in scaling if r["pct_ncrit"] == 100][0]
        at_150 = [r for r in scaling if r["pct_ncrit"] == 150][0]
        degradation = at_100["real"] - at_150["real"]

        if degradation > 0.3:
            analysis["findings"].append(
                f"Sharp degradation beyond N_crit: -{degradation*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                f"Graceful degradation beyond N_crit: -{degradation*100:.0f}%"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2075: Capacity Scaling with True Entropy")
    print("=" * 60)
    print()

    exp = CapacityScalingTrueEntropy()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2075_capacity_scaling.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
