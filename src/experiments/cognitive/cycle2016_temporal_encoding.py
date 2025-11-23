"""
Cycle 2016: Temporal Encoding in Holographic Memory
====================================================
Testing how well holographic memory preserves temporal sequences.

Question: Can we encode and retrieve ordered sequences?

Method:
1. Encode sequence A→B→C→D as chained bindings
2. Test forward retrieval (given A, get D)
3. Test positional queries (what's at position 3?)
4. Compare with random order (control)

This relates to Temporal Stewardship - encoding patterns for future systems.
"""

import numpy as np
import json
from datetime import datetime

class TemporalEncoding:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        # Fixed position markers
        np.random.seed(42)
        self.positions = [self._generate() for _ in range(10)]
        np.random.seed(None)

    def _generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v / np.linalg.norm(v)

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def encode_sequence(self, items):
        """Encode sequence as superposition of position-bound items."""
        trace = np.zeros(self.d)
        for i, item in enumerate(items):
            bound = self._circ_conv(self.positions[i], item)
            trace += bound
        return self._normalize(trace)

    def retrieve_at_position(self, trace, position):
        """Retrieve item at given position."""
        return self._circ_corr(trace, self.positions[position])

    def run(self):
        print("Cycle 2016: Temporal Encoding")
        print("-" * 50)

        # Test sequences of different lengths
        results = []

        for seq_len in [3, 5, 7]:
            correct = 0
            total_sim = 0.0

            for _ in range(self.num_trials):
                # Generate sequence
                items = [self._generate() for _ in range(seq_len)]

                # Encode
                trace = self.encode_sequence(items)

                # Test retrieval at each position
                pos_correct = 0
                pos_sim = 0.0

                for pos in range(seq_len):
                    retrieved = self.retrieve_at_position(trace, pos)
                    retrieved = self._normalize(retrieved)
                    sim = np.dot(retrieved, items[pos])
                    pos_sim += sim
                    if sim > 0.3:
                        pos_correct += 1

                # Trial success if all positions correct
                if pos_correct == seq_len:
                    correct += 1
                total_sim += pos_sim / seq_len

            acc = correct / self.num_trials
            avg_sim = total_sim / self.num_trials

            results.append({
                "length": seq_len,
                "accuracy": acc,
                "avg_similarity": avg_sim
            })

            print(f"Length {seq_len}: {acc*100:.0f}% accuracy (sim={avg_sim:.4f})")

        print()

        # Compare with storage capacity findings
        print("Comparison with storage capacity (C2008):")
        print("  Storage limit: ~5 items")
        print("  Sequence encoding: Uses same mechanism")
        print("  Expected degradation above 5 items")

        return results

if __name__ == "__main__":
    exp = TemporalEncoding()
    results = exp.run()

    output = {
        "cycle": 2016,
        "experiment": "Temporal Encoding",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Position markers enable sequence storage",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2016_temporal_encoding.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
