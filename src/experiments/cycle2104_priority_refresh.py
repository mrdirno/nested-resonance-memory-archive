"""
Cycle 2104: Priority-Based Refresh Test
=======================================
Some items may be more important than others.

Test: Give high-priority items 3× refresh rate.
- High priority: refreshed 3× per cycle
- Low priority: refreshed 1× per cycle

Does this improve high-priority accuracy without destroying low-priority?
"""

import numpy as np
import json
from datetime import datetime

class PriorityRefreshTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _hash_key(self, key, k_memories):
        return int(abs(key[0]) * 1000) % k_memories

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, n_items, n_high_priority, seed):
        """Run with priority refresh."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []
        priorities = []  # True = high, False = low

        # Store items (first n_high_priority are high)
        for i in range(n_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)
            is_high = i < n_high_priority

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value, is_high))

            keys.append(key)
            values.append(value)
            priorities.append(is_high)

        codebook = values.copy()

        # Priority-based maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                mem_items = memory_items[mem_idx]
                if not mem_items:
                    continue

                # Add noise
                noise = np.random.normal(0, 0.01, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                # Refresh based on priority
                for key, value, is_high in mem_items:
                    # High priority: 3× more likely to refresh
                    refresh_prob = 0.3 if is_high else 0.1
                    if np.random.random() < refresh_prob:
                        binding = self._circ_conv(key, value)
                        memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

        # Test by priority
        high_correct = 0
        low_correct = 0

        for key, value, is_high in zip(keys, values, priorities):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                if is_high:
                    high_correct += 1
                else:
                    low_correct += 1

        high_acc = high_correct / n_high_priority if n_high_priority > 0 else 0
        low_acc = low_correct / (n_items - n_high_priority) if (n_items - n_high_priority) > 0 else 0

        return high_acc, low_acc

    def run_experiment(self):
        """Test priority refresh configurations."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Total':<8} {'High':<8} {'Low':<8} {'High%':<10} {'Low%':<10}")
        print("-" * 45)

        # Test different priority splits
        test_cases = [
            (60, 10),   # 10 high, 50 low
            (60, 20),   # 20 high, 40 low
            (60, 30),   # 30 high, 30 low
            (80, 20),   # 20 high, 60 low
        ]

        for n_items, n_high in test_cases:
            n_low = n_items - n_high
            high_accs = []
            low_accs = []

            for trial in range(self.num_trials):
                high, low = self.run_trial(n_items, n_high, seed=trial*100+n_items)
                high_accs.append(high)
                low_accs.append(low)

            mean_high = np.mean(high_accs)
            mean_low = np.mean(low_accs)

            results["tests"].append({
                "n_total": n_items,
                "n_high": n_high,
                "n_low": n_low,
                "high_accuracy": float(mean_high),
                "low_accuracy": float(mean_low)
            })

            print(f"{n_items:<8} {n_high:<8} {n_low:<8} {mean_high*100:>5.0f}%{'':<4} {mean_low*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate priority benefit."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check if high priority gets better accuracy
        avg_high = np.mean([t["high_accuracy"] for t in tests])
        avg_low = np.mean([t["low_accuracy"] for t in tests])

        diff = avg_high - avg_low

        if diff > 0.1:
            analysis["findings"].append(
                f"Priority refresh works: High {avg_high*100:.0f}% vs Low {avg_low*100:.0f}% (+{diff*100:.0f}%)"
            )
            analysis["priority_works"] = True
        elif diff > 0:
            analysis["findings"].append(
                f"Marginal priority benefit: +{diff*100:.0f}%"
            )
            analysis["priority_works"] = True
        else:
            analysis["findings"].append(
                "Priority refresh has no effect"
            )
            analysis["priority_works"] = False

        # Check if low priority is still acceptable
        if avg_low >= 0.8:
            analysis["findings"].append(
                "Low priority items still maintain 80%+ accuracy"
            )
        elif avg_low >= 0.6:
            analysis["findings"].append(
                f"Low priority items degrade to {avg_low*100:.0f}%"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2104: Priority-Based Refresh Test")
    print("=" * 60)
    print()

    exp = PriorityRefreshTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2104_priority_refresh.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
