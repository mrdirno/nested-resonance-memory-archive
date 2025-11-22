"""
Cycle 2083: Warmup Acceleration
===============================
C2082 showed need for ~100 cycle warmup before deployment.

Question: Can stronger initial Hebbian reduce warmup time?
Test: Start with higher strength, decay to 0.5×
"""

import numpy as np
import json
import psutil
from datetime import datetime

class WarmupAcceleration:
    def __init__(self):
        self.dimension = 1024
        self.n_items = int(0.0140 * self.dimension)
        self.num_cycles = 300
        self.measurement_interval = 20
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

    def run_trial(self, warmup_strategy, seed):
        """Run with given warmup strategy."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create and store patterns
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
        accuracy_history = []

        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            # Calculate Hebbian strength based on strategy
            if warmup_strategy == "constant":
                strength = 0.5
            elif warmup_strategy == "decay":
                # Start at 2.0, decay to 0.5 over 100 cycles
                if cycle < 100:
                    strength = 2.0 - 1.5 * (cycle / 100)
                else:
                    strength = 0.5
            elif warmup_strategy == "burst":
                # High strength for first 50 cycles only
                strength = 2.0 if cycle < 50 else 0.5
            else:
                strength = 0.5

            # Hebbian refresh
            idx = cycle % self.n_items
            binding = self._circ_conv(keys[idx], values[idx])
            memory = self._normalize(memory + strength * binding)

            # Measure accuracy
            if cycle % self.measurement_interval == 0:
                correct = 0
                for key, value in zip(keys, values):
                    key_inv = np.roll(key[::-1], 1)
                    retrieved = self._circ_conv(memory, key_inv)
                    retrieved = self._cleanup(retrieved, codebook)
                    if np.dot(retrieved, value) > 0.5:
                        correct += 1
                accuracy = correct / self.n_items
                accuracy_history.append({
                    "cycle": cycle,
                    "accuracy": float(accuracy)
                })

        return accuracy_history

    def run_experiment(self):
        """Test different warmup strategies."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "strategies": []
        }

        print(f"Testing warmup strategies with {self.n_items} items")
        print()
        print(f"{'Strategy':<12} {'Cycle 0':<12} {'Cycle 40':<12} {'Cycle 100':<12} {'Final':<12}")
        print("-" * 60)

        for strategy in ["constant", "decay", "burst"]:
            all_histories = []

            for trial in range(self.num_trials):
                history = self.run_trial(strategy, seed=trial*100)
                all_histories.append(history)

            # Aggregate
            cycles = [h["cycle"] for h in all_histories[0]]
            aggregated = []

            for i, cycle in enumerate(cycles):
                accs = [all_histories[t][i]["accuracy"] for t in range(self.num_trials)]
                aggregated.append({
                    "cycle": cycle,
                    "mean_accuracy": float(np.mean(accs))
                })

            results["strategies"].append({
                "strategy": strategy,
                "aggregated": aggregated
            })

            # Find key timepoints
            c0 = aggregated[0]["mean_accuracy"]
            c40 = [a for a in aggregated if a["cycle"] == 40][0]["mean_accuracy"]
            c100 = [a for a in aggregated if a["cycle"] == 100][0]["mean_accuracy"]
            final = aggregated[-1]["mean_accuracy"]

            print(f"{strategy:<12} {c0*100:<12.0f}% {c40*100:<12.0f}% {c100*100:<12.0f}% {final*100:<12.0f}%")

        return results

    def analyze(self, results):
        """Find best warmup strategy."""
        strategies = results["strategies"]
        analysis = {"findings": []}

        # Find first cycle to reach 80% for each strategy
        warmup_times = {}
        for s in strategies:
            for a in s["aggregated"]:
                if a["mean_accuracy"] >= 0.8:
                    warmup_times[s["strategy"]] = a["cycle"]
                    break
            else:
                warmup_times[s["strategy"]] = self.num_cycles

        best = min(warmup_times, key=warmup_times.get)
        constant_time = warmup_times.get("constant", self.num_cycles)
        best_time = warmup_times[best]

        if best_time < constant_time:
            analysis["findings"].append(
                f"Warmup accelerated: {best} reaches 80% at cycle {best_time} (vs {constant_time})"
            )
            analysis["speedup"] = constant_time / best_time if best_time > 0 else float('inf')
        else:
            analysis["findings"].append("No warmup acceleration achieved")
            analysis["speedup"] = 1.0

        analysis["best_strategy"] = best
        analysis["warmup_times"] = warmup_times

        # Check final accuracy
        for s in strategies:
            final = s["aggregated"][-1]["mean_accuracy"]
            if final < 0.75:
                analysis["findings"].append(
                    f"Warning: {s['strategy']} ends low at {final*100:.0f}%"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2083: Warmup Acceleration")
    print("=" * 60)
    print()

    exp = WarmupAcceleration()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2083_warmup_acceleration.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
