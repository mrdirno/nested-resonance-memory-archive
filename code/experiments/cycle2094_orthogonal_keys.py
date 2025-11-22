"""
Cycle 2094: Orthogonal Key Generation
=====================================
C2093 found binding interference at storage is the bottleneck.

Hypothesis: Orthogonal keys reduce cross-binding interference.
Test: Gram-Schmidt orthogonalization of random keys.

Compare: Random keys vs Orthogonal keys at various capacities.
"""

import numpy as np
import json
from datetime import datetime

class OrthogonalKeyTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate_random(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _generate_orthogonal_keys(self, d, n):
        """Generate n orthogonal keys using Gram-Schmidt."""
        keys = []
        for i in range(n):
            # Start with random vector
            v = np.random.normal(0, 1.0/np.sqrt(d), d)

            # Orthogonalize against previous keys
            for k in keys:
                v = v - np.dot(v, k) * k

            # Normalize
            norm = np.linalg.norm(v)
            if norm > 1e-10:
                v = v / norm
            else:
                # If vector collapsed, generate new random
                v = np.random.normal(0, 1.0/np.sqrt(d), d)
                v = self._normalize(v)

            keys.append(v)
        return keys

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, orthogonal, seed):
        """Run with random or orthogonal keys."""
        np.random.seed(seed)
        d = self.dimension

        # Generate keys
        if orthogonal:
            keys = self._generate_orthogonal_keys(d, n_items)
        else:
            keys = [self._generate_random(d) for _ in range(n_items)]

        # Generate values (always random)
        values = [self._generate_random(d) for _ in range(n_items)]

        # Store
        memory = np.zeros(d)
        for key, value in zip(keys, values):
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)

        codebook = values.copy()

        # Pre-operation accuracy
        correct_pre = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_pre += 1

        # Operation cycles
        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.01, d)
            memory = self._normalize(memory + noise)

            idx = cycle % n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Post-operation accuracy
        correct_post = 0
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_post += 1

        return correct_pre / n_items, correct_post / n_items

    def run_experiment(self):
        """Compare random vs orthogonal keys."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "comparisons": []
        }

        print(f"D = {self.dimension}, comparing random vs orthogonal keys...")
        print()
        print(f"{'Items':<8} {'Random Pre':<12} {'Orth Pre':<12} {'Random Post':<12} {'Orth Post':<12}")
        print("-" * 60)

        for n_items in [10, 16, 24, 32, 43]:
            random_pre = []
            random_post = []
            orth_pre = []
            orth_post = []

            for trial in range(self.num_trials):
                # Random keys
                pre, post = self.run_trial(n_items, orthogonal=False, seed=trial*100+n_items)
                random_pre.append(pre)
                random_post.append(post)

                # Orthogonal keys
                pre, post = self.run_trial(n_items, orthogonal=True, seed=trial*100+n_items+1000)
                orth_pre.append(pre)
                orth_post.append(post)

            rp_mean = np.mean(random_pre)
            rpost_mean = np.mean(random_post)
            op_mean = np.mean(orth_pre)
            opost_mean = np.mean(orth_post)

            results["comparisons"].append({
                "n_items": n_items,
                "random_pre": float(rp_mean),
                "random_post": float(rpost_mean),
                "orth_pre": float(op_mean),
                "orth_post": float(opost_mean),
                "improvement_pre": float(op_mean - rp_mean),
                "improvement_post": float(opost_mean - rpost_mean)
            })

            print(f"{n_items:<8} {rp_mean*100:>5.0f}%{'':<6} {op_mean*100:>5.0f}%{'':<6} {rpost_mean*100:>5.0f}%{'':<6} {opost_mean*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate orthogonal key benefit."""
        comps = results["comparisons"]
        analysis = {"findings": []}

        # Average improvement
        avg_imp_pre = np.mean([c["improvement_pre"] for c in comps])
        avg_imp_post = np.mean([c["improvement_post"] for c in comps])

        if avg_imp_post > 0.1:
            analysis["findings"].append(
                f"Orthogonal keys improve post-op by +{avg_imp_post*100:.0f}% on average"
            )
            analysis["orthogonal_helps"] = True
        elif avg_imp_post > 0:
            analysis["findings"].append(
                f"Orthogonal keys provide marginal benefit (+{avg_imp_post*100:.0f}%)"
            )
            analysis["orthogonal_helps"] = False
        else:
            analysis["findings"].append(
                "Orthogonal keys do not help (circular convolution breaks orthogonality)"
            )
            analysis["orthogonal_helps"] = False

        # Check if plateau is broken
        high_cap = [c for c in comps if c["n_items"] >= 32]
        if high_cap and any(c["orth_post"] >= 0.8 for c in high_cap):
            analysis["findings"].append(
                "Orthogonal keys BREAK the capacity plateau!"
            )
            analysis["plateau_broken"] = True
        else:
            analysis["findings"].append(
                "Orthogonal keys do not break plateau"
            )
            analysis["plateau_broken"] = False

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2094: Orthogonal Key Generation")
    print("=" * 60)
    print()

    exp = OrthogonalKeyTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2094_orthogonal_keys.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
