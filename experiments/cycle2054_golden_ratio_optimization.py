"""
Cycle 2054: Golden Ratio Parameter Optimization
===============================================
C2053 showed golden ratio control creates deep hierarchies.
Optimize the specific φ-based parameter combinations.
"""

import numpy as np
import json
from datetime import datetime

class GoldenRatioOptimization:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 20
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

    def run_nrm(self, comp_prob, decomp_prob, energy_threshold):
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

            if len(agents) >= 2 and np.random.random() < comp_prob:
                i, j = np.random.choice(len(agents), 2, replace=False)
                new_agent = {
                    "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                    "energy": agents[i]["energy"] + agents[j]["energy"],
                    "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                }
                agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                agents.append(new_agent)

            for i, agent in enumerate(agents):
                if agent["energy"] < energy_threshold and agent["depth"] >= 1:
                    if np.random.random() < decomp_prob:
                        noise = np.random.randn(d) * 0.05
                        child = {
                            "memory": self._normalize(agent["memory"] + noise),
                            "energy": agent["energy"] / 2,
                            "depth": max(0, agent["depth"] - 1)
                        }
                        agents[i] = child
                        agents.append(child.copy())

            for agent in agents:
                agent["energy"] *= 0.99

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "pop": len(agents),
            "max_depth": max([a["depth"] for a in agents]) if agents else 0,
            "avg_depth": np.mean([a["depth"] for a in agents]) if agents else 0
        }

    def run(self):
        print("Cycle 2054: Golden Ratio Parameter Optimization")
        print("-" * 70)

        phi = self.phi

        # Test variations of golden ratio scaling
        configs = [
            # (comp_scale, decomp_scale, thresh_scale, label)
            (0.1, 0.1, 0.5, "Baseline"),
            (0.1*phi, 0.1/phi, 0.5*phi, "C2053 Best"),
            (0.05*phi, 0.05/phi, 0.5*phi, "Half Rate"),
            (0.15*phi, 0.15/phi, 0.5*phi, "1.5x Rate"),
            (0.1*phi, 0.1/phi, 0.3*phi, "Low Thresh"),
            (0.1*phi, 0.1/phi, 0.7*phi, "High Thresh"),
            (0.1*phi**2, 0.1/phi**2, 0.5*phi, "φ² Scaling"),
            (1/phi**3, 1/phi**2, 1/phi, "Pure φ Powers"),
        ]

        results = []

        print(f"{'Configuration':>20} | {'Pop':>6} | {'Avg Depth':>10} | {'Max Depth':>10}")
        print("-" * 70)

        for comp, decomp, thresh, label in configs:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_nrm(comp, decomp, thresh))

            avg = {
                "label": label,
                "comp": comp,
                "decomp": decomp,
                "thresh": thresh,
                "pop": np.mean([r["pop"] for r in trial_results]),
                "avg_depth": np.mean([r["avg_depth"] for r in trial_results]),
                "max_depth": np.mean([r["max_depth"] for r in trial_results])
            }

            results.append(avg)
            print(f"{label:>20} | {avg['pop']:>6.1f} | {avg['avg_depth']:>10.2f} | {avg['max_depth']:>10.1f}")

        print()
        # Find optimal
        best_depth = max(results, key=lambda x: x["avg_depth"])
        print(f"Best avg depth: {best_depth['label']} ({best_depth['avg_depth']:.2f})")

        best_balance = max(results, key=lambda x: x["pop"] * x["avg_depth"])
        print(f"Best balance (pop×depth): {best_balance['label']} ({best_balance['pop']*best_balance['avg_depth']:.1f})")

        return results

if __name__ == "__main__":
    exp = GoldenRatioOptimization()
    results = exp.run()

    output = {
        "cycle": 2054,
        "experiment": "Golden Ratio Optimization",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2054_golden_ratio_optimization.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
