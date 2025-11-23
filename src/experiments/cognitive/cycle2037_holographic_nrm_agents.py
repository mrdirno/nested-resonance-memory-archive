"""
Cycle 2037: Holographic NRM Agents
==================================
Integrate holographic memory into NRM agent framework.
Each agent has holographic memory for state/rules.
Test composition-decomposition with memory.
"""

import numpy as np
import json
from datetime import datetime

class HolographicAgent:
    def __init__(self, dimension=512):
        self.d = dimension
        self.memory = np.zeros(dimension)
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

    def store(self, key, value):
        """Store key-value in memory."""
        binding = self._circ_conv(key, value)
        self.memory = self._normalize(self.memory + binding)

    def retrieve(self, key):
        """Retrieve value by key."""
        retrieved = self._circ_corr(self.memory, key)
        return self._normalize(retrieved)


class HolographicNRM:
    def __init__(self, dimension=512):
        self.d = dimension
        self.num_cycles = 200
        self.num_trials = 20

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def compose(self, agent1, agent2):
        """Compose two agents into one with merged memory."""
        new_agent = HolographicAgent(self.d)
        new_agent.memory = self._normalize(agent1.memory + agent2.memory)
        new_agent.depth = max(agent1.depth, agent2.depth) + 1
        new_agent.energy = agent1.energy + agent2.energy
        return new_agent

    def decompose(self, agent):
        """Decompose agent into two with split memory."""
        child1 = HolographicAgent(self.d)
        child2 = HolographicAgent(self.d)

        # Split memory (simple split + noise)
        noise = np.random.randn(self.d) * 0.1
        child1.memory = self._normalize(agent.memory + noise)
        child2.memory = self._normalize(agent.memory - noise)

        child1.depth = max(0, agent.depth - 1)
        child2.depth = max(0, agent.depth - 1)
        child1.energy = agent.energy / 2
        child2.energy = agent.energy / 2

        return child1, child2

    def test_memory_preservation(self):
        """Test if memory survives composition-decomposition."""
        correct = 0

        for _ in range(self.num_trials):
            # Create agent with stored pattern
            agent1 = HolographicAgent(self.d)
            key = self._generate()
            value = self._generate()
            agent1.store(key, value)

            # Create second agent
            agent2 = HolographicAgent(self.d)
            agent2.store(self._generate(), self._generate())

            # Compose
            composed = self.compose(agent1, agent2)

            # Retrieve from composed
            retrieved = composed.retrieve(key)
            sim = np.dot(retrieved, value)

            if sim > 0.2:  # Lower threshold for merged memory
                correct += 1

        return correct / self.num_trials

    def test_decomposition_memory(self):
        """Test if children retain parent's memory."""
        correct = 0

        for _ in range(self.num_trials):
            # Create agent with pattern
            agent = HolographicAgent(self.d)
            key = self._generate()
            value = self._generate()
            agent.store(key, value)

            # Decompose
            child1, child2 = self.decompose(agent)

            # Both children should retain memory
            sim1 = np.dot(child1.retrieve(key), value)
            sim2 = np.dot(child2.retrieve(key), value)

            if sim1 > 0.2 and sim2 > 0.2:
                correct += 1

        return correct / self.num_trials

    def test_depth_dynamics(self):
        """Test NRM depth dynamics with holographic agents."""
        results = []

        for _ in range(self.num_trials):
            agents = [HolographicAgent(self.d) for _ in range(10)]
            depth_history = []

            for cycle in range(self.num_cycles):
                avg_depth = np.mean([a.depth for a in agents])
                depth_history.append(avg_depth)

                # Composition events
                if len(agents) >= 2 and np.random.random() < 0.1:
                    i, j = np.random.choice(len(agents), 2, replace=False)
                    new_agent = self.compose(agents[i], agents[j])
                    agents = [a for k, a in enumerate(agents) if k not in [i, j]]
                    agents.append(new_agent)

                # Decomposition events
                deep_agents = [i for i, a in enumerate(agents) if a.depth >= 2]
                if deep_agents and np.random.random() < 0.1:
                    idx = np.random.choice(deep_agents)
                    c1, c2 = self.decompose(agents[idx])
                    agents = [a for k, a in enumerate(agents) if k != idx]
                    agents.extend([c1, c2])

                # Cap population
                if len(agents) > 50:
                    agents = list(np.random.choice(agents, 50, replace=False))

            results.append({
                "final_population": len(agents),
                "max_depth": max(a.depth for a in agents),
                "avg_depth": np.mean([a.depth for a in agents])
            })

        return {
            "avg_final_pop": np.mean([r["final_population"] for r in results]),
            "avg_max_depth": np.mean([r["max_depth"] for r in results]),
            "avg_depth": np.mean([r["avg_depth"] for r in results])
        }

    def run(self):
        print("Cycle 2037: Holographic NRM Agents")
        print("-" * 50)

        # Test memory preservation
        comp_acc = self.test_memory_preservation()
        decomp_acc = self.test_decomposition_memory()

        print(f"Memory after composition: {comp_acc*100:.0f}%")
        print(f"Memory after decomposition: {decomp_acc*100:.0f}%")

        # Test dynamics
        dynamics = self.test_depth_dynamics()
        print(f"\nNRM Dynamics:")
        print(f"  Avg final population: {dynamics['avg_final_pop']:.1f}")
        print(f"  Avg max depth: {dynamics['avg_max_depth']:.1f}")
        print(f"  Avg depth: {dynamics['avg_depth']:.2f}")

        return {
            "composition_memory": comp_acc,
            "decomposition_memory": decomp_acc,
            "dynamics": dynamics
        }

if __name__ == "__main__":
    exp = HolographicNRM()
    results = exp.run()

    output = {
        "cycle": 2037,
        "experiment": "Holographic NRM Agents",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2037_holographic_nrm_agents.json"
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {path}")
