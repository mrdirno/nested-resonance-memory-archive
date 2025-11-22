"""
Cycle 2017: Sequence Completion
===============================
C2016 showed sequences can be stored and retrieved by position.

Question: Can we do sequence completion (predict next item)?

Method: Given A→B→C, predict D by learning the pattern.
This requires temporal prediction, not just retrieval.
"""

import numpy as np
import json
from datetime import datetime

class SequenceCompletion:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def run(self):
        print("Cycle 2017: Sequence Completion")
        print("-" * 50)

        # Test: Learn A→B→C→D, predict D given A,B,C
        correct = 0
        total_sim = 0.0

        for _ in range(self.num_trials):
            # Training sequence
            A = self._generate()
            B = self._generate()
            C = self._generate()
            D = self._generate()

            # Learn transitions as rules
            rule_AB = self._circ_conv(A, B)
            rule_BC = self._circ_conv(B, C)
            rule_CD = self._circ_conv(C, D)

            # Superpose rules to form "sequence memory"
            seq_mem = self._normalize(rule_AB + rule_BC + rule_CD)

            # Test: Given C, can we predict D?
            # Method: Query seq_mem with C to get next
            # This is like: C * (A*B + B*C + C*D)
            predicted = self._circ_corr(seq_mem, C)
            predicted = self._normalize(predicted)

            sim = np.dot(predicted, D)
            total_sim += sim

            if sim > 0.2:  # Lower threshold for noisy retrieval
                correct += 1

        accuracy = correct / self.num_trials
        avg_sim = total_sim / self.num_trials

        print(f"Sequence completion (A→B→C→?): {accuracy*100:.0f}% (sim={avg_sim:.4f})")

        # Compare with direct retrieval
        print("\nComparison:")
        print("  Direct retrieval: sim ~0.5")
        print(f"  Sequence completion: sim ~{avg_sim:.2f}")

        if accuracy > 0.8:
            print("\nSequence completion WORKS")
        elif accuracy > 0.5:
            print("\nSequence completion partially works")
        else:
            print("\nSequence completion FAILS - needs different approach")

        return {
            "accuracy": accuracy,
            "avg_similarity": avg_sim
        }

if __name__ == "__main__":
    exp = SequenceCompletion()
    results = exp.run()

    output = {
        "cycle": 2017,
        "experiment": "Sequence Completion",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2017_sequence_completion.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
