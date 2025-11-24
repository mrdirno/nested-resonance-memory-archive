"""
Cycle 2084: Dynamic Item Addition
=================================
Test if new items can be added during operation without
breaking existing memories.

Scenario:
1. Start with N/2 items, run warmup
2. Add remaining N/2 items
3. Check if original items still retrievable
"""

import numpy as np
import json
import psutil
from datetime import datetime

class DynamicItemAddition:
    def __init__(self):
        self.dimension = 1024
        self.n_total = int(0.0140 * self.dimension)  # 14 items
        self.warmup_cycles = 100
        self.post_addition_cycles = 200
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
        """Run with dynamic item addition."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        n_initial = self.n_total // 2
        n_new = self.n_total - n_initial

        # Create initial items
        memory = np.zeros(d)
        keys = []
        values = []

        for _ in range(n_initial):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Warmup phase
        for cycle in range(self.warmup_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % n_initial
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Measure accuracy before addition
        correct = 0
        for key, value in zip(keys[:n_initial], values[:n_initial]):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1
        pre_addition_acc = correct / n_initial

        # Add new items
        for _ in range(n_new):
            key = self._generate(d)
            value = self._generate(d)
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)
            values.append(value)
            codebook.append(value)

        # Post-addition operation
        for cycle in range(self.post_addition_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % self.n_total
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + 0.5 * binding)

        # Measure final accuracy for original items
        correct_original = 0
        for key, value in zip(keys[:n_initial], values[:n_initial]):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_original += 1
        original_acc = correct_original / n_initial

        # Measure accuracy for new items
        correct_new = 0
        for key, value in zip(keys[n_initial:], values[n_initial:]):
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct_new += 1
        new_acc = correct_new / n_new if n_new > 0 else 0

        return {
            "pre_addition_accuracy": pre_addition_acc,
            "original_items_accuracy": original_acc,
            "new_items_accuracy": new_acc
        }

    def run_experiment(self):
        """Test dynamic addition."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_total": self.n_total,
                "n_initial": self.n_total // 2,
                "n_new": self.n_total - self.n_total // 2,
                "warmup_cycles": self.warmup_cycles,
                "post_cycles": self.post_addition_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "trials": []
        }

        pre_accs = []
        orig_accs = []
        new_accs = []

        for trial in range(self.num_trials):
            result = self.run_trial(seed=trial*100)
            results["trials"].append(result)
            pre_accs.append(result["pre_addition_accuracy"])
            orig_accs.append(result["original_items_accuracy"])
            new_accs.append(result["new_items_accuracy"])

        results["summary"] = {
            "mean_pre_addition": float(np.mean(pre_accs)),
            "mean_original_after": float(np.mean(orig_accs)),
            "mean_new_items": float(np.mean(new_accs))
        }

        n_initial = self.n_total // 2
        n_new = self.n_total - n_initial

        print(f"Starting with {n_initial} items, adding {n_new} items")
        print()
        print(f"{'Metric':<25} {'Accuracy':<12}")
        print("-" * 40)
        print(f"{'Pre-addition (N/2)':<25} {results['summary']['mean_pre_addition']*100:.0f}%")
        print(f"{'Original items after':<25} {results['summary']['mean_original_after']*100:.0f}%")
        print(f"{'New items after':<25} {results['summary']['mean_new_items']*100:.0f}%")

        return results

    def analyze(self, results):
        """Analyze dynamic addition impact."""
        summary = results["summary"]
        analysis = {"findings": []}

        # Check if original items preserved
        degradation = summary["mean_pre_addition"] - summary["mean_original_after"]

        if abs(degradation) < 0.1:
            analysis["findings"].append(
                f"Original items preserved: {summary['mean_original_after']*100:.0f}% (Δ = {-degradation*100:.0f}%)"
            )
            analysis["originals_preserved"] = True
        else:
            analysis["findings"].append(
                f"Original items degraded: {summary['mean_pre_addition']*100:.0f}% → {summary['mean_original_after']*100:.0f}%"
            )
            analysis["originals_preserved"] = False

        # Check if new items learned
        if summary["mean_new_items"] >= 0.8:
            analysis["findings"].append(
                f"New items learned: {summary['mean_new_items']*100:.0f}%"
            )
            analysis["new_learned"] = True
        else:
            analysis["findings"].append(
                f"New items not fully learned: {summary['mean_new_items']*100:.0f}%"
            )
            analysis["new_learned"] = False

        # Overall viability
        if analysis.get("originals_preserved") and analysis.get("new_learned"):
            analysis["findings"].append("Dynamic addition is viable")
        else:
            analysis["findings"].append("Dynamic addition has limitations")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2084: Dynamic Item Addition")
    print("=" * 60)
    print()

    exp = DynamicItemAddition()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2084_dynamic_addition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
