"""
Cycle 2112: Similarity Search Test
==================================
Can we find keys similar to a query?

Method: Query with a noisy/modified version of a key.
The system should still retrieve the correct value.

This tests the system's tolerance to approximate queries.
"""

import numpy as np
import json
from datetime import datetime

class SimilaritySearchTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
        self.num_cycles = 200
        self.n_items = 50

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

    def _add_noise_to_key(self, key, noise_level):
        """Add noise to create similar but not identical key."""
        noise = np.random.normal(0, noise_level, len(key))
        noisy_key = self._normalize(key + noise)
        return noisy_key

    def run_trial(self, noise_level, seed):
        """Test retrieval with noisy queries."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Store items
        for _ in range(self.n_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

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

        # Test with noisy queries
        correct = 0
        for key, value in zip(keys, values):
            # Create noisy version of key
            noisy_key = self._add_noise_to_key(key, noise_level)

            # Use original memory location
            mem_idx = self._hash_key(key, self.k_memories)

            # Query with noisy key
            noisy_inv = np.roll(noisy_key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], noisy_inv)
            retrieved = self._cleanup(retrieved, codebook)

            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / self.n_items

    def run_experiment(self):
        """Test various noise levels for similarity search."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "n_items": self.n_items,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "noise_levels": []
        }

        print(f"D={self.dimension}, K={self.k_memories}, {self.n_items} items")
        print()
        print(f"{'Query Noise':<15} {'Accuracy':<12} {'Key Sim':<12}")
        print("-" * 40)

        noise_levels = [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

        for noise in noise_levels:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(noise, seed=trial*100+int(noise*100))
                accs.append(acc)

            mean_acc = np.mean(accs)

            # Estimate key similarity at this noise level
            key_sim = 1.0 / (1.0 + noise**2)  # Approximate

            results["noise_levels"].append({
                "noise": noise,
                "accuracy": float(mean_acc),
                "est_key_sim": float(key_sim)
            })

            print(f"{noise:<15} {mean_acc*100:>5.0f}%{'':<6} ~{key_sim:.2f}")

        return results

    def analyze(self, results):
        """Evaluate similarity search capability."""
        levels = results["noise_levels"]
        analysis = {"findings": []}

        # Find max noise for 80% accuracy
        for level in levels:
            if level["accuracy"] < 0.8:
                prev = levels[levels.index(level) - 1]
                analysis["findings"].append(
                    f"80% threshold: noise = {prev['noise']}-{level['noise']}"
                )
                break

        # Check if any noise tolerance
        l01 = [l for l in levels if l["noise"] == 0.1][0]
        if l01["accuracy"] >= 0.9:
            analysis["findings"].append(
                f"Good tolerance: 10% noise gives {l01['accuracy']*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                f"Limited tolerance: 10% noise gives {l01['accuracy']*100:.0f}%"
            )

        # Compare to exact
        exact = [l for l in levels if l["noise"] == 0][0]
        l03 = [l for l in levels if l["noise"] == 0.3][0]
        if l03["accuracy"] >= exact["accuracy"] - 0.2:
            analysis["findings"].append(
                "System tolerates moderate query noise"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2112: Similarity Search Test")
    print("=" * 60)
    print()

    exp = SimilaritySearchTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2112_similarity_search.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
