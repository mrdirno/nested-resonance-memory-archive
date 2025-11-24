"""
Cycle 2055: Golden Ratio Long-Term Dynamics
==========================================
Test golden ratio control over extended timescales.
Compare stability with baseline over 2000 cycles.
"""

import numpy as np
import json
from datetime import datetime

class GoldenDynamics:
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

    def run_extended(self, comp_prob, decomp_prob, energy_threshold):
        d = self.base_dimension
        agents = []

        for _ in range(15):
            agent = {"memory": np.zeros(d), "energy": 1.0, "depth": 0}
            key = self._generate(d)
            value = self._generate(d)
            agent["memory"] = self._normalize(self._circ_conv(key, value))
            agents.append(agent)

        metrics = {"depth": [], "pop": [], "energy": []}

        for cycle in range(self.num_cycles):
            if not agents:
                break

            # Record metrics every 100 cycles
            if cycle % 100 == 0:
                metrics["depth"].append(np.mean([a["depth"] for a in agents]))
                metrics["pop"].append(len(agents))
                metrics["energy"].append(np.mean([a["energy"] for a in agents]))

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

        return metrics

    def run(self):
        print("Cycle 2055: Golden Ratio Long-Term Dynamics")
        print("-" * 60)

        phi = self.phi

        configs = [
            (0.10, 0.10, 0.5, "Baseline"),
            (0.1*phi, 0.1/phi, 0.3*phi, "Golden Optimal"),
        ]

        results = {}

        for comp, decomp, thresh, label in configs:
            all_metrics = []
            for _ in range(self.num_trials):
                metrics = self.run_extended(comp, decomp, thresh)
                all_metrics.append(metrics)

            # Average across trials
            avg_depth = np.mean([m["depth"] for m in all_metrics], axis=0)
            avg_pop = np.mean([m["pop"] for m in all_metrics], axis=0)

            results[label] = {
                "depth_trajectory": avg_depth.tolist(),
                "pop_trajectory": avg_pop.tolist(),
                "final_depth": avg_depth[-1] if len(avg_depth) > 0 else 0,
                "final_pop": avg_pop[-1] if len(avg_pop) > 0 else 0,
                "depth_stability": np.std(avg_depth[-5:]) if len(avg_depth) >= 5 else 0
            }

            print(f"\n{label}:")
            print(f"  Final depth: {results[label]['final_depth']:.2f}")
            print(f"  Final pop: {results[label]['final_pop']:.1f}")
            print(f"  Stability (std last 5): {results[label]['depth_stability']:.3f}")

        # Comparison
        print("\nLong-Term Comparison:")
        base = results["Baseline"]
        gold = results["Golden Optimal"]
        depth_gain = gold["final_depth"] - base["final_depth"]
        stability_gain = base["depth_stability"] - gold["depth_stability"]
        print(f"  Depth gain: {depth_gain:+.2f}")
        print(f"  Stability gain: {stability_gain:+.3f}")

        return results

if __name__ == "__main__":
    exp = GoldenDynamics()
    results = exp.run()

    output = {
        "cycle": 2055,
        "experiment": "Golden Dynamics",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2055_golden_dynamics.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
