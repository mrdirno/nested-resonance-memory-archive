"""
Cycle 2050: Depth vs Population Tradeoff
========================================
C2049 showed adaptive scaling enables depth but reduces population.
Explore the tradeoff space: can we optimize for different objectives?
"""

import numpy as np
import json
from datetime import datetime

class DepthPopulationTradeoff:
    def __init__(self):
        self.num_cycles = 500
        self.num_trials = 20
        # Different composition probabilities to control depth/pop balance
        self.comp_probs = [0.05, 0.10, 0.15, 0.20, 0.30]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def capacity_for_dim(self, d):
        return int(2.25 * np.sqrt(d))

    def dim_for_capacity(self, capacity):
        return min(4096, max(128, int((capacity / 2.25) ** 2)))

    def run_simulation(self, comp_prob):
        """Run adaptive NRM with given composition probability."""
        agents = []
        for _ in range(20):  # Start with more agents
            d = 128
            agent = {
                "d": d,
                "memory": np.zeros(d),
                "stored": 0,
                "capacity": self.capacity_for_dim(d),
                "depth": 0
            }
            for _ in range(2):
                key = self._generate(d)
                value = self._generate(d)
                binding = self._circ_conv(key, value)
                agent["memory"] = self._normalize(agent["memory"] + binding)
                agent["stored"] += 1
            agents.append(agent)

        for cycle in range(self.num_cycles):
            if len(agents) < 2:
                break

            # Composition
            if np.random.random() < comp_prob and len(agents) >= 2:
                i, j = np.random.choice(len(agents), 2, replace=False)
                combined_stored = agents[i]["stored"] + agents[j]["stored"]
                required_d = self.dim_for_capacity(combined_stored)

                new_agent = {
                    "d": required_d,
                    "memory": np.zeros(required_d),  # Simplified - just track structure
                    "stored": combined_stored,
                    "capacity": self.capacity_for_dim(required_d),
                    "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                }

                agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                agents.append(new_agent)

            # Decomposition (lower rate)
            deep = [i for i, a in enumerate(agents) if a["depth"] >= 2]
            if deep and np.random.random() < 0.05:
                idx = np.random.choice(deep)
                agent = agents[idx]

                child = {
                    "d": agent["d"],
                    "memory": np.zeros(agent["d"]),
                    "stored": agent["stored"],
                    "capacity": agent["capacity"],
                    "depth": max(0, agent["depth"] - 1)
                }

                agents = [a for k, a in enumerate(agents) if k != idx]
                agents.extend([child, child.copy()])

            if len(agents) > 100:
                keep = np.random.choice(len(agents), 100, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "pop": len(agents),
            "max_depth": max([a["depth"] for a in agents]) if agents else 0,
            "avg_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "total_stored": sum([a["stored"] for a in agents]) if agents else 0
        }

    def run(self):
        print("Cycle 2050: Depth vs Population Tradeoff")
        print("-" * 70)

        results = []

        print(f"{'Comp Prob':>10} | {'Pop':>6} | {'Avg Depth':>10} | {'Max Depth':>10} | {'Total Mem':>10}")
        print("-" * 70)

        for prob in self.comp_probs:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_simulation(prob))

            avg = {
                "comp_prob": prob,
                "pop": np.mean([r["pop"] for r in trial_results]),
                "avg_depth": np.mean([r["avg_depth"] for r in trial_results]),
                "max_depth": np.mean([r["max_depth"] for r in trial_results]),
                "total_stored": np.mean([r["total_stored"] for r in trial_results])
            }

            results.append(avg)
            print(f"{prob:>10.2f} | {avg['pop']:>6.1f} | {avg['avg_depth']:>10.2f} | {avg['max_depth']:>10.1f} | {avg['total_stored']:>10.0f}")

        print()
        # Analysis
        print("Tradeoff Analysis:")

        # Find optimal for different objectives
        max_pop = max(results, key=lambda x: x["pop"])
        max_depth = max(results, key=lambda x: x["avg_depth"])
        max_memory = max(results, key=lambda x: x["total_stored"])

        print(f"  Max population: prob={max_pop['comp_prob']} → {max_pop['pop']:.0f} agents")
        print(f"  Max depth: prob={max_depth['comp_prob']} → {max_depth['avg_depth']:.1f} avg depth")
        print(f"  Max total memory: prob={max_memory['comp_prob']} → {max_memory['total_stored']:.0f} items")

        # Composite score
        print("\nComposite Score (pop × depth):")
        for r in results:
            score = r["pop"] * r["avg_depth"]
            print(f"  prob={r['comp_prob']}: {score:.1f}")

        return results

if __name__ == "__main__":
    exp = DepthPopulationTradeoff()
    results = exp.run()

    output = {
        "cycle": 2050,
        "experiment": "Depth Population Tradeoff",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2050_depth_population_tradeoff.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
