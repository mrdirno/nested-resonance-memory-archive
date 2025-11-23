"""
Cycle 2019: Temporal Composition in NRM
=======================================
Connect temporal encoding to NRM composition-decomposition dynamics.

Question: Can temporal sequences represent composition events?

Concept:
- Agent A and Agent B compose → Agent C (depth increase)
- Encode as A + B → C transition
- Test if we can predict composition outcomes

This bridges cognitive capabilities to NRM framework.
"""

import numpy as np
import json
from datetime import datetime

class TemporalComposition:
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
        print("Cycle 2019: Temporal Composition in NRM")
        print("-" * 50)

        correct_comp = 0
        correct_decomp = 0

        for _ in range(self.num_trials):
            # Define agents
            A = self._generate()
            B = self._generate()
            C = self._generate()  # Result of A+B composition

            # Composition rule: A * B → C
            # Encode as: (A+B) binds to C
            AB = self._normalize(A + B)
            comp_rule = self._circ_conv(AB, C)

            # Test: Given A+B, can we predict C?
            predicted_C = self._circ_corr(comp_rule, AB)
            predicted_C = self._normalize(predicted_C)

            sim_comp = np.dot(predicted_C, C)
            if sim_comp > 0.3:
                correct_comp += 1

            # Decomposition: Given C, can we recover A+B?
            # Rule: C binds to (A+B)
            decomp_rule = self._circ_conv(C, AB)

            # Test: Given C, get A+B
            predicted_AB = self._circ_corr(decomp_rule, C)
            predicted_AB = self._normalize(predicted_AB)

            sim_decomp = np.dot(predicted_AB, AB)
            if sim_decomp > 0.3:
                correct_decomp += 1

        acc_comp = correct_comp / self.num_trials
        acc_decomp = correct_decomp / self.num_trials

        print(f"Composition (A+B → C): {acc_comp*100:.0f}%")
        print(f"Decomposition (C → A+B): {acc_decomp*100:.0f}%")

        print()
        print("NRM Connection:")
        print("  Composition = Agent merging (depth increase)")
        print("  Decomposition = Agent splitting (burst events)")
        print("  Both operations can be learned temporally")

        return {
            "composition_accuracy": acc_comp,
            "decomposition_accuracy": acc_decomp
        }

if __name__ == "__main__":
    exp = TemporalComposition()
    results = exp.run()

    output = {
        "cycle": 2019,
        "experiment": "Temporal Composition",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "NRM composition-decomposition can be encoded temporally",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2019_temporal_composition.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
