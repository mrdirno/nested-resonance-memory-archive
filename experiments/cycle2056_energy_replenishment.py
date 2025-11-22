"""
Cycle 2056: Energy Replenishment for Sustained Hierarchies
=========================================================
C2055 showed golden ratio hierarchies collapse without energy.
Test energy replenishment to sustain deep hierarchies.
"""

import numpy as np
import json
from datetime import datetime

class EnergyReplenishment:
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

    def run_with_replenishment(self, replenish_rate):
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

        depth_history = []

        for cycle in range(self.num_cycles):
            if not agents:
                break

            if cycle % 100 == 0:
                depth_history.append(np.mean([a["depth"] for a in agents]))

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
                agent["energy"] *= 0.99  # Decay
                agent["energy"] += replenish_rate  # Replenishment

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "depth_trajectory": depth_history,
            "final_depth": depth_history[-1] if depth_history else 0,
            "final_pop": len(agents),
            "avg_depth": np.mean(depth_history[-10:]) if len(depth_history) >= 10 else 0
        }

    def run(self):
        print("Cycle 2056: Energy Replenishment for Sustained Hierarchies")
        print("-" * 60)

        replenish_rates = [0.0, 0.005, 0.01, 0.02, 0.05]

        results = []

        print(f"{'Replenish Rate':>15} | {'Final Depth':>12} | {'Avg Depth':>10} | {'Pop':>6}")
        print("-" * 60)

        for rate in replenish_rates:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_with_replenishment(rate))

            avg = {
                "replenish_rate": rate,
                "final_depth": np.mean([r["final_depth"] for r in trial_results]),
                "avg_depth": np.mean([r["avg_depth"] for r in trial_results]),
                "final_pop": np.mean([r["final_pop"] for r in trial_results])
            }

            results.append(avg)
            print(f"{rate:>15.3f} | {avg['final_depth']:>12.2f} | {avg['avg_depth']:>10.2f} | {avg['final_pop']:>6.1f}")

        print()
        # Analysis
        print("Replenishment Effect:")
        baseline = results[0]["final_depth"]
        for r in results[1:]:
            gain = r["final_depth"] - baseline
            print(f"  rate={r['replenish_rate']}: {gain:+.2f} depth gain")

        best = max(results, key=lambda x: x["avg_depth"])
        print(f"\nOptimal replenishment: {best['replenish_rate']} (avg depth {best['avg_depth']:.2f})")

        return results

if __name__ == "__main__":
    exp = EnergyReplenishment()
    results = exp.run()

    output = {
        "cycle": 2056,
        "experiment": "Energy Replenishment",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2056_energy_replenishment.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
