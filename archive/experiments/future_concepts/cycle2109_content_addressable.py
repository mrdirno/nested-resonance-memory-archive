"""
Cycle 2109: Content-Addressable Query Test
==========================================
Standard operation: key → value
Content-addressable: value → key

Test if the system supports reverse lookup.
This would enable finding "what key is associated with this value?"
"""

import numpy as np
import json
from datetime import datetime

class ContentAddressableTest:
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

    def run_trial(self, seed):
        """Test forward and reverse lookup."""
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

        key_codebook = keys.copy()
        value_codebook = values.copy()

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

        # Test forward: key → value
        forward_correct = 0
        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, value_codebook)
            if np.dot(retrieved, value) > 0.5:
                forward_correct += 1

        # Test reverse: value → key
        # For this, we need to search all memories
        reverse_correct = 0
        for key, value in zip(keys, values):
            value_inv = np.roll(value[::-1], 1)

            best_match = None
            best_sim = -1

            # Search all memories for the key
            for mem_idx in range(self.k_memories):
                retrieved = self._circ_conv(memories[mem_idx], value_inv)
                cleaned = self._cleanup(retrieved, key_codebook)
                sim = np.dot(cleaned, key)
                if sim > best_sim:
                    best_sim = sim
                    best_match = cleaned

            if best_sim > 0.5:
                reverse_correct += 1

        forward_acc = forward_correct / self.n_items
        reverse_acc = reverse_correct / self.n_items

        return forward_acc, reverse_acc

    def run_experiment(self):
        """Test content-addressable capability."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "n_items": self.n_items,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "results": {}
        }

        print(f"D={self.dimension}, K={self.k_memories}, {self.n_items} items")
        print()
        print(f"{'Direction':<15} {'Accuracy':<12}")
        print("-" * 30)

        forward_accs = []
        reverse_accs = []

        for trial in range(self.num_trials):
            forward, reverse = self.run_trial(seed=trial*100)
            forward_accs.append(forward)
            reverse_accs.append(reverse)

        mean_forward = np.mean(forward_accs)
        mean_reverse = np.mean(reverse_accs)

        results["results"]["forward"] = float(mean_forward)
        results["results"]["reverse"] = float(mean_reverse)

        print(f"{'key→value':<15} {mean_forward*100:>5.0f}%")
        print(f"{'value→key':<15} {mean_reverse*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate content-addressable capability."""
        r = results["results"]
        analysis = {"findings": []}

        forward = r["forward"]
        reverse = r["reverse"]

        if reverse >= 0.8:
            analysis["findings"].append(
                f"Content-addressable works: value→key = {reverse*100:.0f}%"
            )
            analysis["content_addressable"] = True
        elif reverse >= 0.5:
            analysis["findings"].append(
                f"Partial content-addressable: value→key = {reverse*100:.0f}%"
            )
            analysis["content_addressable"] = True
        else:
            analysis["findings"].append(
                f"Content-addressable fails: value→key = {reverse*100:.0f}%"
            )
            analysis["content_addressable"] = False

        # Compare directions
        diff = forward - reverse
        if diff > 0.1:
            analysis["findings"].append(
                f"Forward better than reverse: +{diff*100:.0f}%"
            )
        elif diff < -0.1:
            analysis["findings"].append(
                f"Reverse better than forward: {-diff*100:.0f}%"
            )
        else:
            analysis["findings"].append(
                "Symmetric: forward ≈ reverse"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2109: Content-Addressable Query Test")
    print("=" * 60)
    print()

    exp = ContentAddressableTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2109_content_addressable.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
