"""
Cycle 2045: NRM Capacity Stress Test
====================================
Push agents to capacity limits and observe system behavior.
"""

import numpy as np
import json
from datetime import datetime

class CapacityStressNRM:
    def __init__(self):
        self.base_dimension = 512
        self.num_cycles = 300
        self.num_trials = 20

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_stress(self, initial_memories_per_agent):
        """Run with varying initial memory load."""
        agents = []

        for _ in range(10):
            agent = {
                "d": self.base_dimension,
                "memory": np.zeros(self.base_dimension),
                "stored": 0,
                "capacity": int(2.25 * np.sqrt(self.base_dimension)),
                "depth": 0
            }

            # Load agent with memories
            for _ in range(initial_memories_per_agent):
                key = self._generate(agent["d"])
                value = self._generate(agent["d"])
                binding = np.real(np.fft.ifft(
                    np.fft.fft(key) * np.fft.fft(value)
                ))
                agent["memory"] = self._normalize(agent["memory"] + binding)
                agent["stored"] += 1

            agents.append(agent)

        composition_blocked = 0
        compositions_done = 0

        for cycle in range(self.num_cycles):
            if len(agents) < 2:
                break

            # Composition attempts
            if np.random.random() < 0.15:  # Higher composition rate
                i, j = np.random.choice(len(agents), 2, replace=False)
                combined_stored = agents[i]["stored"] + agents[j]["stored"]
                new_capacity = agents[i]["capacity"]  # Same dimension

                if combined_stored <= new_capacity:
                    # Composition allowed
                    new_agent = {
                        "d": self.base_dimension,
                        "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                        "stored": combined_stored,
                        "capacity": new_capacity,
                        "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                    }
                    agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                    agents.append(new_agent)
                    compositions_done += 1
                else:
                    # Blocked due to capacity
                    composition_blocked += 1

            # Decomposition
            deep = [i for i, a in enumerate(agents) if a["depth"] >= 2]
            if deep and np.random.random() < 0.1:
                idx = np.random.choice(deep)
                agent = agents[idx]

                noise = np.random.randn(agent["d"]) * 0.05
                child1 = {
                    "d": agent["d"],
                    "memory": self._normalize(agent["memory"] + noise),
                    "stored": agent["stored"],
                    "capacity": agent["capacity"],
                    "depth": max(0, agent["depth"] - 1)
                }
                child2 = {
                    "d": agent["d"],
                    "memory": self._normalize(agent["memory"] - noise),
                    "stored": agent["stored"],
                    "capacity": agent["capacity"],
                    "depth": max(0, agent["depth"] - 1)
                }

                agents = [a for k, a in enumerate(agents) if k != idx]
                agents.extend([child1, child2])

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "final_pop": len(agents),
            "final_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "final_usage": np.mean([a["stored"]/a["capacity"] for a in agents]) if agents else 0,
            "compositions_done": compositions_done,
            "compositions_blocked": composition_blocked
        }

    def run(self):
        print("Cycle 2045: NRM Capacity Stress Test")
        print("-" * 70)

        results = []
        memory_loads = [5, 15, 25, 35, 45]  # Out of capacity=50

        print(f"{'Init Load':>10} | {'Final Pop':>10} | {'Depth':>6} | {'Usage':>8} | {'Done':>6} | {'Blocked':>8}")
        print("-" * 70)

        for load in memory_loads:
            trial_results = []
            for _ in range(self.num_trials):
                trial_results.append(self.run_stress(load))

            avg_pop = np.mean([r["final_pop"] for r in trial_results])
            avg_depth = np.mean([r["final_depth"] for r in trial_results])
            avg_usage = np.mean([r["final_usage"] for r in trial_results])
            avg_done = np.mean([r["compositions_done"] for r in trial_results])
            avg_blocked = np.mean([r["compositions_blocked"] for r in trial_results])

            results.append({
                "initial_load": load,
                "final_pop": avg_pop,
                "final_depth": avg_depth,
                "final_usage": avg_usage,
                "compositions_done": avg_done,
                "compositions_blocked": avg_blocked
            })

            print(f"{load:>10} | {avg_pop:>10.1f} | {avg_depth:>6.2f} | {avg_usage*100:>7.1f}% | {avg_done:>6.1f} | {avg_blocked:>8.1f}")

        print()
        # Analysis
        print("Stress Analysis:")
        low_load = results[0]
        high_load = results[-1]
        block_increase = high_load["compositions_blocked"] - low_load["compositions_blocked"]
        print(f"  Blocked compositions increase: {block_increase:.1f}x at high load")

        return results

if __name__ == "__main__":
    exp = CapacityStressNRM()
    results = exp.run()

    output = {
        "cycle": 2045,
        "experiment": "Capacity Stress NRM",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2045_capacity_stress_nrm.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
