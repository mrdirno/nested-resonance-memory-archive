"""
Cycle 2085: Intentional Forgetting
==================================
Test if items can be intentionally forgotten to make room for new ones.

Approach: Stop refreshing an item (remove from Hebbian cycle).
Does it fade from memory while others remain?
"""

import numpy as np
import json
import psutil
from datetime import datetime

class IntentionalForgetting:
    def __init__(self):
        self.dimension = 1024
        self.n_items = 10  # Use composition-safe limit
        self.warmup_cycles = 100
        self.forgetting_cycles = 200
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

    def run_trial(self, seed):
        """Run with intentional forgetting."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Warmup phase - refresh all items
        for cycle in range(self.warmup_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % self.n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Measure accuracy before forgetting
        pre_forget_accs = []
        for key, value in zip(keys, values):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            pre_forget_accs.append(np.dot(retrieved, value))

        # Forgetting phase - stop refreshing first 2 items
        forget_indices = [0, 1]
        active_indices = [i for i in range(self.n_items) if i not in forget_indices]

        for cycle in range(self.forgetting_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Only refresh active items
            idx = active_indices[cycle % len(active_indices)]
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Measure final accuracy
        forgotten_acc = []
        retained_acc = []

        for i, (key, value) in enumerate(zip(keys, values)):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            similarity = np.dot(retrieved, value)

            if i in forget_indices:
                forgotten_acc.append(similarity)
            else:
                retained_acc.append(similarity)

        return {
            "pre_forget_mean": float(np.mean(pre_forget_accs)),
            "forgotten_items_sim": float(np.mean(forgotten_acc)),
            "retained_items_sim": float(np.mean(retained_acc)),
            "forgotten_success": float(np.mean([1 if s > 0.5 else 0 for s in forgotten_acc])),
            "retained_success": float(np.mean([1 if s > 0.5 else 0 for s in retained_acc]))
        }

    def run_experiment(self):
        """Test intentional forgetting."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "n_forgotten": 2,
                "warmup_cycles": self.warmup_cycles,
                "forgetting_cycles": self.forgetting_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "trials": []
        }

        pre_accs = []
        forgotten_sims = []
        retained_sims = []
        forgotten_succs = []
        retained_succs = []

        for trial in range(self.num_trials):
            result = self.run_trial(seed=trial*100)
            results["trials"].append(result)
            pre_accs.append(result["pre_forget_mean"])
            forgotten_sims.append(result["forgotten_items_sim"])
            retained_sims.append(result["retained_items_sim"])
            forgotten_succs.append(result["forgotten_success"])
            retained_succs.append(result["retained_success"])

        results["summary"] = {
            "mean_pre_forget": float(np.mean(pre_accs)),
            "mean_forgotten_similarity": float(np.mean(forgotten_sims)),
            "mean_retained_similarity": float(np.mean(retained_sims)),
            "mean_forgotten_success": float(np.mean(forgotten_succs)),
            "mean_retained_success": float(np.mean(retained_succs))
        }

        print(f"Testing forgetting of 2 items from {self.n_items}")
        print()
        print(f"{'Metric':<25} {'Value':<12}")
        print("-" * 40)
        print(f"{'Pre-forget accuracy':<25} {results['summary']['mean_pre_forget']:.2f}")
        print(f"{'Forgotten items sim':<25} {results['summary']['mean_forgotten_similarity']:.2f}")
        print(f"{'Retained items sim':<25} {results['summary']['mean_retained_similarity']:.2f}")
        print(f"{'Forgotten success rate':<25} {results['summary']['mean_forgotten_success']*100:.0f}%")
        print(f"{'Retained success rate':<25} {results['summary']['mean_retained_success']*100:.0f}%")

        return results

    def analyze(self, results):
        """Analyze forgetting effectiveness."""
        summary = results["summary"]
        analysis = {"findings": []}

        # Check if forgetting works
        if summary["mean_forgotten_success"] < 0.3:
            analysis["findings"].append(
                f"Forgetting works: {summary['mean_forgotten_success']*100:.0f}% retrievable (target < 30%)"
            )
            analysis["forgetting_works"] = True
        else:
            analysis["findings"].append(
                f"Incomplete forgetting: {summary['mean_forgotten_success']*100:.0f}% still retrievable"
            )
            analysis["forgetting_works"] = False

        # Check if retained items preserved
        if summary["mean_retained_success"] >= 0.9:
            analysis["findings"].append(
                f"Retained items preserved: {summary['mean_retained_success']*100:.0f}%"
            )
            analysis["retention_works"] = True
        else:
            analysis["findings"].append(
                f"Collateral damage: only {summary['mean_retained_success']*100:.0f}% retained"
            )
            analysis["retention_works"] = False

        # Overall viability
        if analysis.get("forgetting_works") and analysis.get("retention_works"):
            analysis["findings"].append("Selective forgetting is viable for memory management")
        elif analysis.get("retention_works"):
            analysis["findings"].append("Items persist without refresh - forgetting is slow")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2085: Intentional Forgetting")
    print("=" * 60)
    print()

    exp = IntentionalForgetting()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2085_intentional_forgetting.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
