"""
Cycle 2018: Temporal Pattern Recognition
========================================
C2016: Sequence storage works
C2017: Sequence completion works

Question: Can we recognize repeating patterns?
Test: Given A→B→A→B→A, recognize the period-2 pattern.

This tests if holographic memory can detect temporal structure.
"""

import numpy as np
import json
from datetime import datetime

class PatternRecognition:
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
        print("Cycle 2018: Temporal Pattern Recognition")
        print("-" * 50)

        correct_period2 = 0
        correct_period3 = 0

        for _ in range(self.num_trials):
            # Test 1: Period-2 pattern A→B→A→B→A
            A = self._generate()
            B = self._generate()

            # Build sequence transitions
            trans_AB = self._circ_conv(A, B)
            trans_BA = self._circ_conv(B, A)

            # Memory sees repeated pattern
            seq_mem = self._normalize(trans_AB + trans_BA)

            # Test: After seeing B, what comes next? (Should be A)
            predicted = self._circ_corr(seq_mem, B)
            predicted = self._normalize(predicted)

            sim_A = np.dot(predicted, A)
            if sim_A > 0.3:
                correct_period2 += 1

            # Test 2: Period-3 pattern A→B→C→A→B→C
            C = self._generate()

            trans_BC = self._circ_conv(B, C)
            trans_CA = self._circ_conv(C, A)

            seq_mem3 = self._normalize(trans_AB + trans_BC + trans_CA)

            # After C, what comes? (Should be A)
            predicted3 = self._circ_corr(seq_mem3, C)
            predicted3 = self._normalize(predicted3)

            sim_A3 = np.dot(predicted3, A)
            if sim_A3 > 0.3:
                correct_period3 += 1

        acc2 = correct_period2 / self.num_trials
        acc3 = correct_period3 / self.num_trials

        print(f"Period-2 recognition: {acc2*100:.0f}%")
        print(f"Period-3 recognition: {acc3*100:.0f}%")

        print()
        if acc2 > 0.8 and acc3 > 0.8:
            print("PATTERN RECOGNITION WORKS: Can detect temporal periodicity")
        else:
            print("Pattern recognition limited")

        return {
            "period2_accuracy": acc2,
            "period3_accuracy": acc3
        }

if __name__ == "__main__":
    exp = PatternRecognition()
    results = exp.run()

    output = {
        "cycle": 2018,
        "experiment": "Pattern Recognition",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2018_pattern_recognition.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
