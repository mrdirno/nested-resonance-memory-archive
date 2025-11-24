"""
Cycle 2124: Partition Load Balancing
====================================
Does uneven distribution across partitions affect performance?

Real hash functions may not distribute evenly.
Test robustness to skewed distributions.
"""

import numpy as np
import json
from datetime import datetime

class PartitionBalance:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3
        self.num_cycles = 200

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

    def run_trial(self, n_items, distribution, seed):
        """Test with given partition distribution."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Generate items with specified distribution
        for i in range(n_items):
            key = self._generate(d)
            value = self._generate(d)

            # Assign to partition based on distribution
            if distribution == "uniform":
                mem_idx = i % self.k_memories
            elif distribution == "skewed_2x":
                # First 2 partitions get 2x items
                weights = [2, 2, 1, 1, 1, 1, 0.5, 0.5]
                mem_idx = np.random.choice(self.k_memories, p=np.array(weights)/sum(weights))
            elif distribution == "skewed_4x":
                # First partition gets 4x items
                weights = [4, 1, 1, 1, 1, 1, 0.5, 0.5]
                mem_idx = np.random.choice(self.k_memories, p=np.array(weights)/sum(weights))
            elif distribution == "concentrated":
                # All items in 2 partitions
                mem_idx = i % 2
            else:
                mem_idx = i % self.k_memories

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test
        correct = 0
        for i, (key, value) in enumerate(zip(keys, values)):
            # Find correct partition
            for mem_idx in range(self.k_memories):
                if any(np.allclose(k, key) for k, v in memory_items[mem_idx]):
                    break

            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        accuracy = correct / n_items

        # Calculate load balance
        loads = [len(memory_items[i]) for i in range(self.k_memories)]
        imbalance = np.std(loads) / np.mean(loads) if np.mean(loads) > 0 else 0

        return accuracy, imbalance, loads

    def run_experiment(self):
        """Test different distributions."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        n_items = 80  # Near capacity

        print(f"D={self.dimension}, K={self.k_memories}, N={n_items}")
        print()
        print(f"{'Distribution':<15} {'Imbalance':<12} {'Accuracy':<10} {'Max Load':<10}")
        print("-" * 50)

        distributions = ["uniform", "skewed_2x", "skewed_4x", "concentrated"]

        for dist in distributions:
            accs = []
            imbalances = []
            max_loads = []

            for trial in range(self.num_trials):
                acc, imbalance, loads = self.run_trial(n_items, dist, seed=trial*100)
                accs.append(acc)
                imbalances.append(imbalance)
                max_loads.append(max(loads))

            mean_acc = np.mean(accs)
            mean_imbalance = np.mean(imbalances)
            mean_max_load = np.mean(max_loads)

            results["measurements"].append({
                "distribution": dist,
                "mean_imbalance": float(mean_imbalance),
                "mean_accuracy": float(mean_acc),
                "mean_max_load": float(mean_max_load)
            })

            print(f"{dist:<15} {mean_imbalance:>8.2f}{'':<3} {mean_acc*100:>5.0f}%{'':<3} {mean_max_load:>5.0f}")

        return results

    def analyze(self, results):
        """Analyze balance impact."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Compare uniform to others
        uniform = next((m for m in measurements if m["distribution"] == "uniform"), None)
        if uniform:
            for m in measurements:
                if m["distribution"] != "uniform":
                    diff = (m["mean_accuracy"] - uniform["mean_accuracy"]) * 100
                    analysis["findings"].append(
                        f"{m['distribution']}: {diff:+.0f}% vs uniform"
                    )

        # Check if concentrated fails
        concentrated = next((m for m in measurements if m["distribution"] == "concentrated"), None)
        if concentrated:
            if concentrated["mean_accuracy"] < 0.5:
                analysis["findings"].append(
                    f"Concentrated distribution fails: {concentrated['mean_accuracy']*100:.0f}%"
                )
            else:
                analysis["findings"].append(
                    f"System tolerates extreme concentration: {concentrated['mean_accuracy']*100:.0f}%"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2124: Partition Load Balancing")
    print("=" * 60)
    print()

    exp = PartitionBalance()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2124_partition_balance.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
