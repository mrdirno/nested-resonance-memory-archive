"""
Cycle 2044: NRM with Capacity-Aware Memory
==========================================
Apply C2043 capacity formula to NRM agent implementation.
Agents have dimensioned memory based on capacity requirements.
"""

import numpy as np
import json
from datetime import datetime

class CapacityAwareAgent:
    def __init__(self, dimension, capacity_target):
        self.d = dimension
        self.capacity = int(2.25 * np.sqrt(dimension))  # C2043 formula
        self.memory = np.zeros(dimension)
        self.stored_count = 0
        self.depth = 0
        self.energy = 1.0

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def can_store(self):
        return self.stored_count < self.capacity

    def store(self, key, value):
        if not self.can_store():
            return False
        binding = self._circ_conv(key, value)
        self.memory = self._normalize(self.memory + binding)
        self.stored_count += 1
        return True

    def retrieve(self, key):
        return self._normalize(self._circ_corr(self.memory, key))


class NRMWithCapacity:
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

    def compose(self, agent1, agent2):
        """Compose with capacity-aware memory merge."""
        new_d = max(agent1.d, agent2.d)
        new_agent = CapacityAwareAgent(new_d, 0)

        # Merge memories (resize if needed)
        if agent1.d == agent2.d:
            new_agent.memory = self._normalize(agent1.memory + agent2.memory)
        else:
            # Pad smaller to match larger
            if agent1.d > agent2.d:
                padded = np.zeros(agent1.d)
                padded[:agent2.d] = agent2.memory
                new_agent.memory = self._normalize(agent1.memory + padded)
            else:
                padded = np.zeros(agent2.d)
                padded[:agent1.d] = agent1.memory
                new_agent.memory = self._normalize(agent2.memory + padded)

        new_agent.stored_count = agent1.stored_count + agent2.stored_count
        new_agent.depth = max(agent1.depth, agent2.depth) + 1
        new_agent.energy = agent1.energy + agent2.energy

        return new_agent

    def run_simulation(self):
        """Run NRM dynamics with capacity tracking."""
        agents = [CapacityAwareAgent(self.base_dimension, 0) for _ in range(10)]

        # Give each agent some initial memories
        for agent in agents:
            for _ in range(3):
                key = self._generate(agent.d)
                value = self._generate(agent.d)
                agent.store(key, value)

        metrics = {
            "depth_history": [],
            "population_history": [],
            "capacity_usage": []
        }

        for cycle in range(self.num_cycles):
            if not agents:
                break

            avg_depth = np.mean([a.depth for a in agents])
            avg_usage = np.mean([a.stored_count / a.capacity for a in agents])

            metrics["depth_history"].append(avg_depth)
            metrics["population_history"].append(len(agents))
            metrics["capacity_usage"].append(avg_usage)

            # Composition
            if len(agents) >= 2 and np.random.random() < 0.1:
                i, j = np.random.choice(len(agents), 2, replace=False)
                new_agent = self.compose(agents[i], agents[j])

                # Check if merged memory exceeds capacity
                if new_agent.stored_count <= new_agent.capacity:
                    agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                    agents.append(new_agent)
                # Else: composition blocked due to capacity

            # Decomposition
            deep = [i for i, a in enumerate(agents) if a.depth >= 2]
            if deep and np.random.random() < 0.1:
                idx = np.random.choice(deep)
                agent = agents[idx]

                child1 = CapacityAwareAgent(agent.d, 0)
                child2 = CapacityAwareAgent(agent.d, 0)

                # Split memory
                noise = np.random.randn(agent.d) * 0.05
                child1.memory = self._normalize(agent.memory + noise)
                child2.memory = self._normalize(agent.memory - noise)
                child1.stored_count = agent.stored_count
                child2.stored_count = agent.stored_count
                child1.depth = max(0, agent.depth - 1)
                child2.depth = max(0, agent.depth - 1)

                agents = [a for k, a in enumerate(agents) if k != idx]
                agents.extend([child1, child2])

            # Population cap
            if len(agents) > 50:
                agents = list(np.random.choice(agents, 50, replace=False))

        return metrics

    def run(self):
        print("Cycle 2044: NRM with Capacity-Aware Memory")
        print("-" * 60)

        all_metrics = []

        for _ in range(self.num_trials):
            metrics = self.run_simulation()
            all_metrics.append(metrics)

        # Aggregate
        avg_final_depth = np.mean([m["depth_history"][-1] if m["depth_history"] else 0 for m in all_metrics])
        avg_final_pop = np.mean([m["population_history"][-1] if m["population_history"] else 0 for m in all_metrics])
        avg_capacity_usage = np.mean([np.mean(m["capacity_usage"]) if m["capacity_usage"] else 0 for m in all_metrics])

        print(f"Results over {self.num_trials} trials:")
        print(f"  Final avg depth: {avg_final_depth:.2f}")
        print(f"  Final population: {avg_final_pop:.1f}")
        print(f"  Avg capacity usage: {avg_capacity_usage*100:.1f}%")

        print(f"\nCapacity Formula Applied:")
        print(f"  Base d={self.base_dimension} → capacity={int(2.25*np.sqrt(self.base_dimension))}")

        return {
            "avg_final_depth": avg_final_depth,
            "avg_final_pop": avg_final_pop,
            "avg_capacity_usage": avg_capacity_usage,
            "base_dimension": self.base_dimension,
            "base_capacity": int(2.25 * np.sqrt(self.base_dimension))
        }

if __name__ == "__main__":
    exp = NRMWithCapacity()
    results = exp.run()

    output = {
        "cycle": 2044,
        "experiment": "NRM with Capacity Limits",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2044_nrm_with_capacity_limits.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
