"""
Cycle 2002: Multi-Step Deductive Reasoning
==========================================
C310 showed single-step deduction works (A→B, given A, derive B).

Question: Can holographic memory chain multiple steps?
A→B, B→C: Given A, can we derive C?

Method: Compose rules, then apply.
If Rule1 = A*B and Rule2 = B*C
Then Chain = Rule1 * B^-1 * Rule2 = A*C
"""

import numpy as np
import json
from datetime import datetime

class MultiStepDeduction:
    def __init__(self, dimension=2048):
        self.d = dimension

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def encode_rule(self, ant, con):
        return self._circ_conv(ant, con)

    def chain_rules(self, rule1, rule2, intermediate):
        """Chain Rule1 and Rule2 by removing intermediate.
        Chain = Rule1 * B^-1 * Rule2"""
        # Unbind intermediate from rule1: A*B * B^-1 = A
        first = self._circ_corr(rule1, intermediate)
        # Unbind intermediate from rule2: B*C * B^-1 = C
        second = self._circ_corr(rule2, intermediate)
        # Combine: A * C
        return self._circ_conv(first, second)

    def deduce(self, rule, fact):
        """Deduce consequence from rule given fact."""
        return self._circ_conv(rule, fact)

class MultiStepExperiment:
    def __init__(self):
        self.mem = MultiStepDeduction(dimension=2048)
        self.num_trials = 50

    def run(self):
        print("Cycle 2002: Multi-Step Deductive Reasoning")
        print("-" * 50)

        correct_single = 0
        correct_chain = 0
        total_single = 0.0
        total_chain = 0.0

        for i in range(self.num_trials):
            # Concepts: Socrates → Human → Mortal
            A = self.mem.generate()  # Socrates
            B = self.mem.generate()  # Human
            C = self.mem.generate()  # Mortal
            D = self.mem.generate()  # Random

            # Rules
            Rule_AB = self.mem.encode_rule(A, B)  # Socrates → Human
            Rule_BC = self.mem.encode_rule(B, C)  # Human → Mortal

            # Test 1: Single-step (A→B)
            Deduced_B = self.mem.deduce(Rule_AB, A)
            sim_single = np.dot(self.mem._normalize(Deduced_B),
                              self.mem._normalize(B))
            total_single += sim_single
            if sim_single > 0.5:
                correct_single += 1

            # Test 2: Two-step chain (A→B→C)
            Chained_AC = self.mem.chain_rules(Rule_AB, Rule_BC, B)
            Deduced_C = self.mem._circ_corr(Chained_AC, A)
            # Actually, let's try direct composition
            # Given A, apply both rules in sequence
            Step1 = self.mem._circ_corr(Rule_AB, A)  # Should give B
            Step2 = self.mem._circ_corr(Rule_BC, Step1)  # Should give C

            sim_chain = np.dot(self.mem._normalize(Step2),
                             self.mem._normalize(C))
            total_chain += sim_chain

            # Invalid check
            sim_invalid = np.dot(self.mem._normalize(Step2),
                               self.mem._normalize(D))

            if sim_chain > 0.3 and abs(sim_invalid) < 0.2:
                correct_chain += 1

            if i == 0:
                print("\nTrial 1 Details:")
                print(f"  Chain: A→B→C (Socrates→Human→Mortal)")
                print(f"  Single-step (A→B) sim: {sim_single:.4f}")
                print(f"  Two-step (A→C) sim: {sim_chain:.4f}")
                print(f"  Invalid sim: {sim_invalid:.4f}")

        acc_single = correct_single / self.num_trials
        acc_chain = correct_chain / self.num_trials

        print("\nResults Summary:")
        print(f"Single-step accuracy: {acc_single*100:.1f}% (avg sim: {total_single/self.num_trials:.4f})")
        print(f"Two-step chain accuracy: {acc_chain*100:.1f}% (avg sim: {total_chain/self.num_trials:.4f})")

        print("\nCognitive Track:")
        print("  C310: Single-step deduction (100%)")
        print(f"  C2002: Two-step chain ({acc_chain*100:.0f}%)")

        return {
            "single_step_accuracy": acc_single,
            "chain_accuracy": acc_chain,
            "avg_single_sim": total_single / self.num_trials,
            "avg_chain_sim": total_chain / self.num_trials
        }

if __name__ == "__main__":
    exp = MultiStepExperiment()
    results = exp.run()

    output = {
        "cycle": 2002,
        "experiment": "Multi-Step Deduction",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Holographic memory can chain inference steps",
        "results": results,
        "status": "SUCCESS" if results["chain_accuracy"] > 0.5 else "PARTIAL"
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2002_multistep_deduction.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
