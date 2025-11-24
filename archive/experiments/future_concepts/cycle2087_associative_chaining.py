"""
Cycle 2087: Associative Chaining
================================
Test indirect retrieval through chains.

Store: A→B, B→C
Query: Can we retrieve C from A through B?
"""

import numpy as np
import json
import psutil
from datetime import datetime

class AssociativeChaining:
    def __init__(self):
        self.dimension = 1024
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

    def run_trial(self, chain_length, seed):
        """Test chaining of given length."""
        np.random.seed(seed)
        self._entropy_counter = seed * 1000
        d = self.dimension

        # Create chain: A→B, B→C, C→D, etc.
        chain = [self._generate(d) for _ in range(chain_length + 1)]
        codebook = chain.copy()

        # Store associations
        memory = np.zeros(d)
        keys = []

        for i in range(chain_length):
            key = chain[i]  # A, B, C
            value = chain[i + 1]  # B, C, D
            binding = self._circ_conv(key, value)
            memory = self._normalize(memory + binding)
            keys.append(key)

        # Run operation
        for cycle in range(self.num_cycles):
            noise = self._get_entropy_vector(d)
            memory = self._normalize(memory + noise)

            idx = cycle % chain_length
            binding = self._circ_conv(chain[idx], chain[idx + 1])
            memory = self._normalize(memory + 0.5 * binding)

        # Test direct retrieval (one hop)
        direct_correct = 0
        for i in range(chain_length):
            key_inv = np.roll(chain[i][::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, chain[i + 1]) > 0.5:
                direct_correct += 1
        direct_acc = direct_correct / chain_length

        # Test chained retrieval (A→B→C)
        # Start with A, retrieve B, use B to retrieve C
        chained_correct = 0
        chained_attempts = 0

        for i in range(chain_length - 1):  # Need at least 2 hops
            # First hop: A→B
            key_inv = np.roll(chain[i][::-1], 1)
            intermediate = self._circ_conv(memory, key_inv)
            intermediate = self._cleanup(intermediate, codebook)

            # Second hop: B→C
            int_inv = np.roll(intermediate[::-1], 1)
            final = self._circ_conv(memory, int_inv)
            final = self._cleanup(final, codebook)

            # Check if we got C
            target = chain[i + 2]
            if np.dot(final, target) > 0.5:
                chained_correct += 1
            chained_attempts += 1

        chained_acc = chained_correct / chained_attempts if chained_attempts > 0 else 0

        return {
            "chain_length": chain_length,
            "direct_accuracy": direct_acc,
            "chained_accuracy": chained_acc
        }

    def run_experiment(self):
        """Test different chain lengths."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "chains": []
        }

        print(f"Testing associative chaining")
        print()
        print(f"{'Chain':<10} {'Direct':<12} {'Chained':<12}")
        print("-" * 35)

        for chain_length in [2, 3, 4, 5]:
            direct_accs = []
            chained_accs = []

            for trial in range(self.num_trials):
                result = self.run_trial(chain_length, seed=trial*100+chain_length)
                direct_accs.append(result["direct_accuracy"])
                chained_accs.append(result["chained_accuracy"])

            mean_direct = float(np.mean(direct_accs))
            mean_chained = float(np.mean(chained_accs))

            results["chains"].append({
                "chain_length": chain_length,
                "direct_accuracy": mean_direct,
                "chained_accuracy": mean_chained
            })

            print(f"{chain_length}→{'':<7} {mean_direct*100:<12.0f}% {mean_chained*100:<12.0f}%")

        return results

    def analyze(self, results):
        """Analyze chaining capability."""
        chains = results["chains"]
        analysis = {"findings": []}

        # Check if chaining works
        chain_2 = [c for c in chains if c["chain_length"] == 2][0]
        if chain_2["chained_accuracy"] >= 0.8:
            analysis["findings"].append(
                f"2-hop chaining works: {chain_2['chained_accuracy']*100:.0f}%"
            )
            analysis["chaining_works"] = True
        else:
            analysis["findings"].append(
                f"2-hop chaining limited: {chain_2['chained_accuracy']*100:.0f}%"
            )
            analysis["chaining_works"] = False

        # Compare direct vs chained
        for c in chains:
            gap = c["direct_accuracy"] - c["chained_accuracy"]
            if gap > 0.3:
                analysis["findings"].append(
                    f"Chain {c['chain_length']}: large gap {gap*100:.0f}% (error compounds)"
                )

        # Find max chain length for 50%
        max_chain = 0
        for c in chains:
            if c["chained_accuracy"] >= 0.5:
                max_chain = c["chain_length"]

        if max_chain > 0:
            analysis["findings"].append(f"Max viable chain: {max_chain} hops")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2087: Associative Chaining")
    print("=" * 60)
    print()

    exp = AssociativeChaining()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2087_associative_chaining.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
