"""
Cycle 2000: Analogical Reasoning in Holographic Memory
=====================================================
Building on C310 (Deductive) and C311 (Abductive).

Question: Can holographic memory perform analogical reasoning?
Analogy: A:B :: C:? → Find D such that A*B ≈ C*D

Method: Use relational encoding. If we know "Cat:Animal" and "Dog:?",
can we infer "Dog:Animal" by transferring the relation?

Relation = A^-1 * B (unbind to get the relation)
Prediction = Relation * C (apply relation to new antecedent)
"""

import numpy as np
import json
from datetime import datetime

class HolographicAnalogicalMemory:
    def __init__(self, dimension=2048):
        self.d = dimension

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def extract_relation(self, a, b):
        """R = A^-1 * B (what transforms A into B)"""
        return self._circ_corr(b, a)

    def apply_relation(self, relation, c):
        """D = R * C (apply relation to new element)"""
        return self._circ_conv(relation, c)

class AnalogicalReasoningExperiment:
    def __init__(self):
        self.mem = HolographicAnalogicalMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "analogy_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 2000: Analogical Reasoning Experiment")
        print("-" * 50)

        correct = 0
        total_valid = 0.0
        total_invalid = 0.0

        for i in range(self.num_trials):
            # 1. Define concepts
            Cat = self.mem.generate_vector()
            Dog = self.mem.generate_vector()
            Bird = self.mem.generate_vector()
            Animal = self.mem.generate_vector()
            Plant = self.mem.generate_vector()
            Random = self.mem.generate_vector()

            # 2. Extract relation: "is-a" from Cat:Animal
            Relation = self.mem.extract_relation(Cat, Animal)

            # 3. Apply relation to Dog
            Predicted_Animal = self.mem.apply_relation(Relation, Dog)
            sim_valid = np.dot(self.mem._normalize(Predicted_Animal),
                             self.mem._normalize(Animal))
            total_valid += sim_valid

            # 4. Test cross-talk: Apply to Bird (should also get Animal)
            Predicted_Animal2 = self.mem.apply_relation(Relation, Bird)
            sim_bird = np.dot(self.mem._normalize(Predicted_Animal2),
                            self.mem._normalize(Animal))

            # 5. Invalid tests
            # Apply "is-a" relation to get Plant (wrong)
            sim_plant = np.dot(self.mem._normalize(Predicted_Animal),
                             self.mem._normalize(Plant))
            total_invalid += abs(sim_plant)

            # Apply to Random
            Predicted_Random = self.mem.apply_relation(Relation, Random)
            sim_random = np.dot(self.mem._normalize(Predicted_Random),
                              self.mem._normalize(Animal))
            total_invalid += abs(sim_random)

            # Success if valid analogy strong, invalid analogies weak
            if sim_valid > 0.3 and abs(sim_plant) < 0.2 and abs(sim_random) < 0.2:
                correct += 1

            if i == 0:
                print("\nTrial 1 Details:")
                print(f"  Analogy: Cat:Animal :: Dog:?")
                print(f"  Predicted answer similarity to Animal: {sim_valid:.4f}")
                print(f"  Cross-domain (Bird:?): {sim_bird:.4f}")
                print(f"  Invalid (Dog:Plant?): {sim_plant:.4f}")
                print(f"  Invalid (Random:?): {sim_random:.4f}")

        self.results["analogy_accuracy"] = correct / self.num_trials
        self.results["avg_valid_sim"] = total_valid / self.num_trials
        self.results["avg_invalid_sim"] = total_invalid / (self.num_trials * 2)

        print("\nResults Summary:")
        print(f"Analogy Accuracy: {self.results['analogy_accuracy']*100:.1f}%")
        print(f"Avg Valid Sim:    {self.results['avg_valid_sim']:.4f}")
        print(f"Avg Invalid Sim:  {self.results['avg_invalid_sim']:.4f}")

        # Comparison with C310/C311
        print("\nCognitive Track Comparison:")
        print("  C310 Deductive:  100% (cause→effect)")
        print("  C311 Abductive:  100% (effect→cause)")
        print(f"  C312 Analogical: {self.results['analogy_accuracy']*100:.0f}% (relation transfer)")

        return self.results

if __name__ == "__main__":
    exp = AnalogicalReasoningExperiment()
    results = exp.run()

    output = {
        "cycle": 2000,
        "experiment": "Analogical Reasoning",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Holographic memory can transfer relations across domains",
        "method": "Extract relation via unbinding, apply via binding",
        "results": results,
        "status": "SUCCESS" if results["analogy_accuracy"] > 0.8 else "PARTIAL"
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2000_analogical_reasoning_results.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
