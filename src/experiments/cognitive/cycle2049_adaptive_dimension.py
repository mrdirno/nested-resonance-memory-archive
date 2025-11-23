"""
Cycle 2049: Adaptive Dimension Scaling for NRM
=============================================
Apply C2043 capacity formula to dynamically size agent memory.
Agents grow dimension as memory requirements increase.

capacity = 2.25 * sqrt(d)
=> d = (capacity / 2.25)^2

When agent needs more capacity, increase dimension.
"""

import numpy as np
import json
from datetime import datetime

class AdaptiveDimensionNRM:
    def __init__(self):
        self.min_dimension = 128
        self.max_dimension = 4096
        self.num_cycles = 500
        self.num_trials = 20

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def capacity_for_dim(self, d):
        return int(2.25 * np.sqrt(d))

    def dim_for_capacity(self, capacity):
        return int((capacity / 2.25) ** 2)

    def resize_memory(self, memory, old_d, new_d):
        """Resize memory to new dimension (pad or truncate)."""
        if new_d == old_d:
            return memory
        elif new_d > old_d:
            # Pad with zeros
            new_mem = np.zeros(new_d)
            new_mem[:old_d] = memory
            return self._normalize(new_mem)
        else:
            # Truncate (lossy)
            return self._normalize(memory[:new_d])

    def run_adaptive_simulation(self):
        """Run NRM with adaptive dimension scaling."""
        # Start agents with minimum dimension
        agents = []
        for _ in range(10):
            d = self.min_dimension
            agent = {
                "d": d,
                "memory": np.zeros(d),
                "stored": 0,
                "capacity": self.capacity_for_dim(d),
                "depth": 0,
                "upgrades": 0
            }
            # Initial memories
            for _ in range(3):
                key = self._generate(d)
                value = self._generate(d)
                binding = self._circ_conv(key, value)
                agent["memory"] = self._normalize(agent["memory"] + binding)
                agent["stored"] += 1
            agents.append(agent)

        composition_done = 0
        upgrades_total = 0

        for cycle in range(self.num_cycles):
            if len(agents) < 2:
                break

            # Composition
            if np.random.random() < 0.1:
                i, j = np.random.choice(len(agents), 2, replace=False)
                combined_stored = agents[i]["stored"] + agents[j]["stored"]

                # Determine required dimension
                required_d = self.dim_for_capacity(combined_stored)
                required_d = max(required_d, agents[i]["d"], agents[j]["d"])
                required_d = min(required_d, self.max_dimension)

                # Resize memories if needed
                if agents[i]["d"] != required_d:
                    agents[i]["memory"] = self.resize_memory(
                        agents[i]["memory"], agents[i]["d"], required_d
                    )
                    upgrades_total += 1
                if agents[j]["d"] != required_d:
                    agents[j]["memory"] = self.resize_memory(
                        agents[j]["memory"], agents[j]["d"], required_d
                    )
                    upgrades_total += 1

                # Compose
                new_agent = {
                    "d": required_d,
                    "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                    "stored": combined_stored,
                    "capacity": self.capacity_for_dim(required_d),
                    "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1,
                    "upgrades": agents[i]["upgrades"] + agents[j]["upgrades"]
                }

                agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                agents.append(new_agent)
                composition_done += 1

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
                    "depth": max(0, agent["depth"] - 1),
                    "upgrades": agent["upgrades"]
                }
                child2 = child1.copy()
                child2["memory"] = self._normalize(agent["memory"] - noise)

                agents = [a for k, a in enumerate(agents) if k != idx]
                agents.extend([child1, child2])

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "final_pop": len(agents),
            "final_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "final_avg_dim": np.mean([a["d"] for a in agents]) if agents else 0,
            "final_max_dim": max([a["d"] for a in agents]) if agents else 0,
            "compositions": composition_done,
            "upgrades": upgrades_total
        }

    def run_fixed_simulation(self, fixed_dim):
        """Baseline: fixed dimension (no adaptation)."""
        agents = []
        for _ in range(10):
            agent = {
                "d": fixed_dim,
                "memory": np.zeros(fixed_dim),
                "stored": 0,
                "capacity": self.capacity_for_dim(fixed_dim),
                "depth": 0
            }
            for _ in range(3):
                key = self._generate(fixed_dim)
                value = self._generate(fixed_dim)
                binding = self._circ_conv(key, value)
                agent["memory"] = self._normalize(agent["memory"] + binding)
                agent["stored"] += 1
            agents.append(agent)

        composition_done = 0
        blocked = 0

        for cycle in range(self.num_cycles):
            if len(agents) < 2:
                break

            if np.random.random() < 0.1:
                i, j = np.random.choice(len(agents), 2, replace=False)
                combined = agents[i]["stored"] + agents[j]["stored"]

                if combined <= agents[i]["capacity"]:
                    new_agent = {
                        "d": fixed_dim,
                        "memory": self._normalize(agents[i]["memory"] + agents[j]["memory"]),
                        "stored": combined,
                        "capacity": agents[i]["capacity"],
                        "depth": max(agents[i]["depth"], agents[j]["depth"]) + 1
                    }
                    agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                    agents.append(new_agent)
                    composition_done += 1
                else:
                    blocked += 1

            deep = [i for i, a in enumerate(agents) if a["depth"] >= 2]
            if deep and np.random.random() < 0.1:
                idx = np.random.choice(deep)
                agent = agents[idx]

                noise = np.random.randn(agent["d"]) * 0.05
                child1 = {
                    "d": fixed_dim,
                    "memory": self._normalize(agent["memory"] + noise),
                    "stored": agent["stored"],
                    "capacity": agent["capacity"],
                    "depth": max(0, agent["depth"] - 1)
                }
                child2 = child1.copy()
                child2["memory"] = self._normalize(agent["memory"] - noise)

                agents = [a for k, a in enumerate(agents) if k != idx]
                agents.extend([child1, child2])

            if len(agents) > 50:
                keep = np.random.choice(len(agents), 50, replace=False)
                agents = [agents[k] for k in keep]

        return {
            "final_pop": len(agents),
            "final_depth": np.mean([a["depth"] for a in agents]) if agents else 0,
            "compositions": composition_done,
            "blocked": blocked
        }

    def run(self):
        print("Cycle 2049: Adaptive Dimension Scaling for NRM")
        print("-" * 60)

        # Adaptive
        adaptive_results = []
        for _ in range(self.num_trials):
            adaptive_results.append(self.run_adaptive_simulation())

        avg_adaptive = {
            "pop": np.mean([r["final_pop"] for r in adaptive_results]),
            "depth": np.mean([r["final_depth"] for r in adaptive_results]),
            "avg_dim": np.mean([r["final_avg_dim"] for r in adaptive_results]),
            "max_dim": np.mean([r["final_max_dim"] for r in adaptive_results]),
            "compositions": np.mean([r["compositions"] for r in adaptive_results]),
            "upgrades": np.mean([r["upgrades"] for r in adaptive_results])
        }

        print("Adaptive Scaling:")
        print(f"  Final pop: {avg_adaptive['pop']:.1f}")
        print(f"  Final depth: {avg_adaptive['depth']:.2f}")
        print(f"  Avg dimension: {avg_adaptive['avg_dim']:.0f}")
        print(f"  Max dimension: {avg_adaptive['max_dim']:.0f}")
        print(f"  Compositions: {avg_adaptive['compositions']:.1f}")
        print(f"  Upgrades: {avg_adaptive['upgrades']:.1f}")

        # Fixed baseline
        fixed_results = []
        for _ in range(self.num_trials):
            fixed_results.append(self.run_fixed_simulation(512))

        avg_fixed = {
            "pop": np.mean([r["final_pop"] for r in fixed_results]),
            "depth": np.mean([r["final_depth"] for r in fixed_results]),
            "compositions": np.mean([r["compositions"] for r in fixed_results]),
            "blocked": np.mean([r["blocked"] for r in fixed_results])
        }

        print("\nFixed d=512:")
        print(f"  Final pop: {avg_fixed['pop']:.1f}")
        print(f"  Final depth: {avg_fixed['depth']:.2f}")
        print(f"  Compositions: {avg_fixed['compositions']:.1f}")
        print(f"  Blocked: {avg_fixed['blocked']:.1f}")

        print("\nComparison:")
        comp_gain = avg_adaptive['compositions'] - avg_fixed['compositions']
        print(f"  Composition gain: {comp_gain:+.1f}")

        return {
            "adaptive": avg_adaptive,
            "fixed": avg_fixed
        }

if __name__ == "__main__":
    exp = AdaptiveDimensionNRM()
    results = exp.run()

    output = {
        "cycle": 2049,
        "experiment": "Adaptive Dimension Scaling",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2049_adaptive_dimension.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
