"""
Cycle 2128: Transcendental Key Generation
=========================================
Connect holographic memory to NRM transcendental substrate.

Test: Do keys generated from π, e, φ sequences perform
differently than random keys?

Hypothesis: Transcendental sequences may have structure
that affects binding/retrieval differently.
"""

import numpy as np
import json
from datetime import datetime

class TranscendentalKeys:
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

    def _generate_random(self, d, seed_offset=0):
        """Generate random key."""
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _generate_transcendental(self, d, base, index):
        """Generate key from transcendental sequence."""
        # Use digits of transcendental number as seed
        if base == "pi":
            # Use π digits
            sequence = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
        elif base == "e":
            # Use e digits
            sequence = [2, 7, 1, 8, 2, 8, 1, 8, 2, 8, 4, 5, 9, 0, 4]
        elif base == "phi":
            # Use φ digits
            sequence = [1, 6, 1, 8, 0, 3, 3, 9, 8, 8, 7, 4, 9, 8, 9]
        else:
            sequence = list(range(15))

        # Create seed from sequence and index
        seed = sum(s * (10 ** i) for i, s in enumerate(sequence[:5])) + index
        np.random.seed(seed % (2**31))

        # Generate with transcendental modulation
        v = np.random.normal(0, 1.0/np.sqrt(d), d)

        # Apply phase shift based on base
        if base == "pi":
            phase = np.pi * (index / 100)
        elif base == "e":
            phase = np.e * (index / 100)
        else:
            phase = ((1 + np.sqrt(5)) / 2) * (index / 100)

        # Modulate
        indices = np.arange(d)
        v = v * np.cos(phase * indices / d)

        return self._normalize(v)

    def run_trial(self, n_items, key_type, seed):
        """Test with given key generation method."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Generate and store
        for i in range(n_items):
            if key_type == "random":
                key = self._generate_random(d)
            else:
                key = self._generate_transcendental(d, key_type, i)

            value = self._generate_random(d)  # Values always random
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

        # Test
        correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1

        return correct / n_items

    def run_experiment(self):
        """Compare key generation methods."""
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

        n_items = 80

        print(f"D={self.dimension}, K={self.k_memories}, N={n_items}")
        print()
        print(f"{'Key Type':<15} {'Accuracy':<10}")
        print("-" * 30)

        for key_type in ["random", "pi", "e", "phi"]:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(n_items, key_type, seed=trial*100)
                accs.append(acc)

            mean_acc = np.mean(accs)
            std_acc = np.std(accs)

            results["measurements"].append({
                "key_type": key_type,
                "mean_accuracy": float(mean_acc),
                "std": float(std_acc)
            })

            print(f"{key_type:<15} {mean_acc*100:>5.0f}% ± {std_acc*100:.1f}%")

        return results

    def analyze(self, results):
        """Analyze transcendental key performance."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        random = next((m for m in measurements if m["key_type"] == "random"), None)

        for m in measurements:
            if m["key_type"] != "random" and random:
                diff = (m["mean_accuracy"] - random["mean_accuracy"]) * 100
                analysis["findings"].append(
                    f"{m['key_type']}: {diff:+.0f}% vs random"
                )

        # Check if any transcendental is better
        transcendentals = [m for m in measurements if m["key_type"] != "random"]
        if transcendentals:
            best = max(transcendentals, key=lambda x: x["mean_accuracy"])
            if best["mean_accuracy"] > random["mean_accuracy"]:
                analysis["findings"].append(
                    f"Best transcendental: {best['key_type']} at {best['mean_accuracy']*100:.0f}%"
                )
            else:
                analysis["findings"].append(
                    "Random keys perform as well or better than transcendental"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2128: Transcendental Key Generation")
    print("=" * 60)
    print()

    exp = TranscendentalKeys()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2128_transcendental_keys.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
