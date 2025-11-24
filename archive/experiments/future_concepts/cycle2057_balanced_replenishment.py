"""
Cycle 2057: Balanced Replenishment
=================================
Find sweet spot between depth and population diversity.
Test micro-replenishment rates.
"""

import numpy as np
import json
from datetime import datetime

class BalancedReplenishment:
    def __init__(self):
        self.num_cycles = 2000
        self.num_trials = 10
        self.base_dimension = 512
        self.phi = (1 + np.sqrt(5)) / 2

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_balanced(self, replenish_rate):
        phi = self.phi
        comp_prob = 0.1 * phi
        decomp_prob = 0.1 / phi
        thresh = 0.3 * phi

        d = self.base_dimension
        agents = []

        for _ in range(15):
            agent = {"memory": np.zeros(d), "energy": 1.0, "depth": 0}
            key = self._generate(d)
            value = self._generate(d)
            agent["memory"] = self._normalize(self._circ_conv(key, value))
            agents.append(agent)

        for cycle in range(self.num_cycles):
            if not agents:
                break

            # Composition
            if len(agents) >= 2 and np.random.random() < comp_prob:
                i, j = np.random.choice(len(agents), 2, replace=False)
                new_agent = {
                    "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                    "energy": agents[i]["energy"] + agents[j]["energy"],
                    "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                }
                agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                agents.append(new_agent)

            # Decomposition
            for i, agent in enumerate(agents):
                if agent["energy"] < thresh and agent["depth"] >= 1:
                    if np.random.random() < decomp_prob:
                        noise = np.random.randn(d) * 0.05
                        child = {
                            "memory": self._normalize(agent["memory"] + noise),
                            "energy": agent["energy"] / 2,
                            "depth": max(0, agent["depth"] - 1)
                        }
                        agents[i] = child
                        agents.append(child.copy())

            # Energy dynamics
            for agent in agents:
                agent["energy"] *= 0.99
                agent["energy"] += replenish_rate

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "final_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "final_pop": len(agents),
            "score": len(agents) * np.mean([a["depth"] for a in agents]) if agents else 0
        }

    def run(self):
        print("Cycle 2057: Balanced Replenishment")
        print("-" * 70)

        # Fine-grained search around transition zone
        rates = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008]

        results = []

        print(f"{'Rate':>8} | {'Depth':>8} | {'Pop':>8} | {'Score (D×P)':>12}")
        print("-" * 70)

        for rate in rates:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_balanced(rate))

            avg = {
                "rate": rate,
                "depth": np.mean([r["final_depth"] for r in trial_results]),
                "pop": np.mean([r["final_pop"] for r in trial_results]),
                "score": np.mean([r["score"] for r in trial_results])
            }

            results.append(avg)
            print(f"{rate:>8.3f} | {avg['depth']:>8.2f} | {avg['pop']:>8.1f} | {avg['score']:>12.1f}")

        print()
        # Find optimal
        best_score = max(results, key=lambda x: x["score"])
        print(f"Optimal balanced: rate={best_score['rate']}")
        print(f"  Depth: {best_score['depth']:.2f}")
        print(f"  Population: {best_score['pop']:.1f}")
        print(f"  Score: {best_score['score']:.1f}")

        return results

if __name__ == "__main__":
    exp = BalancedReplenishment()
    results = exp.run()

    output = {
        "cycle": 2057,
        "experiment": "Balanced Replenishment",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2057_balanced_replenishment.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
