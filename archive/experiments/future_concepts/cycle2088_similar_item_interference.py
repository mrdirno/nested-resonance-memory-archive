"""
Cycle 2088: Similar Item Interference
=====================================
Test how similar stored items affect retrieval.

Previous experiments used random orthogonal items.
Real applications may have similar/correlated items.
"""

import numpy as np
import json
import psutil
from datetime import datetime

class SimilarItemInterference:
    def __init__(self):
        self.dimension = 1024
        self.n_items = 10
        self.num_cycles = 200
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

    def _generate_similar(self, base, similarity, d):
        """Generate vector with given similarity to base."""
        # Random component
        random = np.random.normal(0, 1, d)
        random = random - np.dot(random, base) * base  # Orthogonalize
        random = random / np.linalg.norm(random)

        # Mix base and random to achieve target similarity
        mixed = similarity * base + np.sqrt(1 - similarity**2) * random
        return self._normalize(mixed)

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

    def run_trial(self, key_similarity, seed):
        """Test with keys of given similarity."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Generate first key randomly
        keys = [self._generate(d)]

        # Generate remaining keys with target similarity to first
        for _ in range(self.n_items - 1):
            if key_similarity > 0:
                new_key = self._generate_similar(keys[0], key_similarity, d)
            else:
                new_key = self._generate(d)
            keys.append(new_key)

        # Generate independent values
        values = [self._generate(d) for _ in range(self.n_items)]
        codebook = values.copy()

        # Store
        memory = np.zeros(d)
        for key, value in zip(keys, values):
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)

        # Run operation
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % self.n_items
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

        return correct / self.n_items

    def run_experiment(self):
        """Test different similarity levels."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "n_items": self.n_items,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "similarities": []
        }

        print(f"Testing key similarity effects")
        print()
        print(f"{'Similarity':<12} {'Accuracy':<12}")
        print("-" * 25)

        for sim in [0, 0.1, 0.3, 0.5, 0.7, 0.9]:
            accuracies = []

            for trial in range(self.num_trials):
                acc = self.run_trial(sim, seed=trial*100+int(sim*100))
                accuracies.append(acc)

            mean_acc = float(np.mean(accuracies))
            results["similarities"].append({
                "similarity": sim,
                "accuracy": mean_acc
            })

            print(f"{sim:<12.1f} {mean_acc*100:.0f}%")

        return results

    def analyze(self, results):
        """Find similarity tolerance."""
        sims = results["similarities"]
        analysis = {"findings": []}

        # Find threshold for 80% accuracy
        threshold = None
        for s in sims:
            if s["accuracy"] >= 0.8:
                threshold = s["similarity"]
            else:
                break

        if threshold is not None:
            analysis["findings"].append(
                f"Similarity tolerance: r ≤ {threshold} for 80% accuracy"
            )
            analysis["similarity_threshold"] = threshold
        else:
            analysis["findings"].append("Even random keys degraded")

        # Check degradation pattern
        baseline = [s for s in sims if s["similarity"] == 0][0]["accuracy"]
        high_sim = [s for s in sims if s["similarity"] == 0.9][0]["accuracy"]
        drop = baseline - high_sim

        if drop > 0.3:
            analysis["findings"].append(
                f"High interference at r=0.9: {high_sim*100:.0f}% ({drop*100:.0f}% drop)"
            )
        else:
            analysis["findings"].append(
                f"Robust to similarity: only {drop*100:.0f}% drop at r=0.9"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2088: Similar Item Interference")
    print("=" * 60)
    print()

    exp = SimilarItemInterference()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2088_similar_interference.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
