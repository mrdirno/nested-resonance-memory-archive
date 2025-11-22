"""
Cycle 2003: Three-Step Chain - Finding the Limit
=================================================
C2002 showed two-step works (sim 0.52).
Question: At what depth does chaining fail?

Method: Test 1, 2, 3, 4, 5 step chains
Find the critical depth where accuracy drops below 50%.
"""

import numpy as np
import json
from datetime import datetime

class ChainDepthExperiment:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.num_trials = 50
        self.max_depth = 6

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

    def run(self):
        print("Cycle 2003: Chain Depth Limit Search")
        print("-" * 50)
        print()

        results = []

        for depth in range(1, self.max_depth + 1):
            correct = 0
            total_sim = 0.0

            for _ in range(self.num_trials):
                # Create chain of concepts: C0 → C1 → ... → C_depth
                concepts = [self.generate() for _ in range(depth + 1)]

                # Create rules: C_i → C_{i+1}
                rules = []
                for i in range(depth):
                    rule = self._circ_conv(concepts[i], concepts[i+1])
                    rules.append(rule)

                # Chain inference: Start with C0, apply all rules
                current = concepts[0]
                for i in range(depth):
                    # Apply rule i: current * Rule_i → next concept
                    next_approx = self._circ_corr(rules[i], current)
                    current = next_approx

                # Compare final result with target
                target = concepts[depth]
                sim = np.dot(self._normalize(current), self._normalize(target))
                total_sim += sim

                if sim > 0.3:
                    correct += 1

            accuracy = correct / self.num_trials
            avg_sim = total_sim / self.num_trials

            results.append({
                "depth": depth,
                "accuracy": accuracy,
                "avg_similarity": avg_sim
            })

            status = "✓" if accuracy > 0.5 else "✗"
            print(f"Depth {depth}: Accuracy={accuracy*100:5.1f}%, Sim={avg_sim:.4f} {status}")

        print()
        self._analyze(results)
        return results

    def _analyze(self, results):
        print("-" * 50)
        print("CHAIN DEPTH ANALYSIS")
        print("-" * 50)

        # Find critical depth
        critical = None
        for r in results:
            if r["accuracy"] < 0.5:
                critical = r["depth"]
                break

        if critical:
            print(f"\nCRITICAL DEPTH: {critical} (first depth < 50% accuracy)")
        else:
            print(f"\nNo failure found up to depth {self.max_depth}")

        # Similarity decay rate
        sims = [r["avg_similarity"] for r in results]
        if len(sims) >= 2:
            decay_rate = sims[0] - sims[-1]
            per_step = decay_rate / (len(sims) - 1)
            print(f"Similarity decay: {per_step:.4f} per step")
            if sims[0] > 0:
                steps_to_zero = sims[0] / per_step
                print(f"Extrapolated zero-crossing: ~{steps_to_zero:.0f} steps")

        # Working memory capacity
        working = len([r for r in results if r["accuracy"] > 0.8])
        print(f"\nEffective working memory: {working} steps (>80% accuracy)")

if __name__ == "__main__":
    exp = ChainDepthExperiment(dimension=2048)
    results = exp.run()

    output = {
        "cycle": 2003,
        "experiment": "Chain Depth Limit",
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Chain accuracy degrades with depth",
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2003_chain_depth.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
