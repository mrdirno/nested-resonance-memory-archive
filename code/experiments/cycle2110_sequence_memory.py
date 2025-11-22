"""
Cycle 2110: Sequence Memory Test
================================
Can we store ordered sequences like (A, B, C)?

Method: Use positional binding
- pos_0 ⊛ A
- pos_1 ⊛ B
- pos_2 ⊛ C

Then query: pos_i → element_i
"""

import numpy as np
import json
from datetime import datetime

class SequenceMemoryTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
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

    def run_trial(self, seq_length, num_sequences, seed):
        """Store and retrieve sequences."""
        np.random.seed(seed)
        d = self.dimension

        # Generate position vectors (shared across sequences)
        positions = [self._generate(d) for _ in range(seq_length)]

        # Generate sequences
        sequences = []
        all_elements = []

        for _ in range(num_sequences):
            seq = [self._generate(d) for _ in range(seq_length)]
            sequences.append(seq)
            all_elements.extend(seq)

        # Store each sequence in its own memory
        memories = []
        for seq in sequences:
            memory = np.zeros(d)
            for pos_idx, element in enumerate(seq):
                binding = self._circ_conv(positions[pos_idx], element)
                memory = self._normalize(memory + binding)
            memories.append(memory)

        # Maintenance (for each memory)
        for cycle in range(self.num_cycles):
            for mem_idx, (memory, seq) in enumerate(zip(memories, sequences)):
                noise = np.random.normal(0, 0.005, d)
                memory = self._normalize(memory + noise)

                # Refresh one binding
                pos_idx = cycle % seq_length
                binding = self._circ_conv(positions[pos_idx], seq[pos_idx])
                memory = self._normalize(memory + 0.3 * binding)

                memories[mem_idx] = memory

        # Test retrieval
        correct = 0
        total = 0

        for seq_idx, (memory, seq) in enumerate(zip(memories, sequences)):
            for pos_idx in range(seq_length):
                pos_inv = np.roll(positions[pos_idx][::-1], 1)
                retrieved = self._circ_conv(memory, pos_inv)
                retrieved = self._cleanup(retrieved, all_elements)

                if np.dot(retrieved, seq[pos_idx]) > 0.5:
                    correct += 1
                total += 1

        return correct / total

    def run_experiment(self):
        """Test sequence storage at various lengths."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}")
        print()
        print(f"{'Length':<10} {'Sequences':<12} {'Total Elem':<12} {'Accuracy':<12}")
        print("-" * 50)

        test_cases = [
            (5, 5),    # 25 elements
            (10, 3),   # 30 elements
            (10, 5),   # 50 elements
            (20, 3),   # 60 elements
        ]

        for seq_len, num_seq in test_cases:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(seq_len, num_seq, seed=trial*100+seq_len)
                accs.append(acc)

            mean_acc = np.mean(accs)
            total_elem = seq_len * num_seq

            results["tests"].append({
                "seq_length": seq_len,
                "num_sequences": num_seq,
                "total_elements": total_elem,
                "accuracy": float(mean_acc)
            })

            print(f"{seq_len:<10} {num_seq:<12} {total_elem:<12} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate sequence memory capability."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Check if sequences work
        avg_acc = np.mean([t["accuracy"] for t in tests])

        if avg_acc >= 0.9:
            analysis["findings"].append(
                f"Sequence memory works excellently: {avg_acc*100:.0f}% avg"
            )
        elif avg_acc >= 0.7:
            analysis["findings"].append(
                f"Sequence memory works: {avg_acc*100:.0f}% avg"
            )
        else:
            analysis["findings"].append(
                f"Sequence memory degrades: {avg_acc*100:.0f}% avg"
            )

        # Best configuration
        best = max(tests, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Best: {best['seq_length']}×{best['num_sequences']} at {best['accuracy']*100:.0f}%"
        )

        # Check length scaling
        for t in tests:
            if t["seq_length"] >= 20 and t["accuracy"] >= 0.8:
                analysis["findings"].append(
                    f"Long sequences work: length {t['seq_length']} at {t['accuracy']*100:.0f}%"
                )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2110: Sequence Memory Test")
    print("=" * 60)
    print()

    exp = SequenceMemoryTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2110_sequence_memory.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
