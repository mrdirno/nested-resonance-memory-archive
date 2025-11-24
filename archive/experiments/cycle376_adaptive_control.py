"""
CYCLE 376: Adaptive Emergence Control
Objective: Test closed-loop control where agents dynamically adjust parameters.
Agents increase cohesion when alone, decrease when crowded.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from memory.pattern_memory import PatternMemory

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class AdaptiveAgent(FractalAgent):
    """Agent that adapts cohesion based on local density."""
    def __init__(self, agent_id, pos, energy=1.0, sight_range=20.0,
                 move_speed=2.0, metabolic_rate=0.01):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        # Adaptive parameters
        self.base_cohesion = 0.05
        self.current_cohesion = 0.05
        self.flock_count = 0

    def update(self, sim, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False

        # Count neighbors
        neighbors = [a for a in all_agents if a != self and
                    np.linalg.norm(self.pos - a.pos) < self.sight_range]
        n_neighbors = len(neighbors)

        # ADAPTIVE CONTROL: Adjust cohesion based on local density
        # Alone → increase cohesion (seek others)
        # Crowded → decrease cohesion (spread out)
        if n_neighbors == 0:
            self.current_cohesion = min(0.20, self.current_cohesion * 1.2)
        elif n_neighbors > 5:
            self.current_cohesion = max(0.01, self.current_cohesion * 0.8)
        else:
            # Converge to base
            self.current_cohesion = self.base_cohesion + 0.1 * (self.base_cohesion - self.current_cohesion)

        # Flocking with adaptive cohesion
        if neighbors:
            avg_pos = np.mean([n.pos for n in neighbors], axis=0)
            avg_vel = np.mean([n.vel for n in neighbors], axis=0)
            cohesion = (avg_pos - self.pos) * self.current_cohesion
            alignment = (avg_vel - self.vel) * 0.1
            self.vel = (self.vel + cohesion + alignment).clip(-self.move_speed, self.move_speed)
            if n_neighbors > 2:
                self.flock_count += 1

        # Resource seeking
        closest = min((r for r in resources if r.amount > 0),
                     key=lambda r: np.linalg.norm(self.pos - r.pos), default=None)
        if closest:
            dist = np.linalg.norm(self.pos - closest.pos)
            if dist < self.sight_range * 2:
                attract = (closest.pos - self.pos) * 0.1
                self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
                if dist < 2.0:
                    consumed = min(0.1, closest.amount)
                    self.energy += consumed
                    closest.amount -= consumed

        self.pos = (self.pos + self.vel) % sim.world_size
        return True

class FixedAgent(FractalAgent):
    """Agent with fixed cohesion for comparison."""
    def __init__(self, agent_id, pos, energy=1.0, sight_range=20.0,
                 move_speed=2.0, metabolic_rate=0.01, cohesion=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion = cohesion
        self.flock_count = 0

    def update(self, sim, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False

        neighbors = [a for a in all_agents if a != self and
                    np.linalg.norm(self.pos - a.pos) < self.sight_range]

        if neighbors:
            avg_pos = np.mean([n.pos for n in neighbors], axis=0)
            avg_vel = np.mean([n.vel for n in neighbors], axis=0)
            cohesion = (avg_pos - self.pos) * self.cohesion
            alignment = (avg_vel - self.vel) * 0.1
            self.vel = (self.vel + cohesion + alignment).clip(-self.move_speed, self.move_speed)
            if len(neighbors) > 2:
                self.flock_count += 1

        closest = min((r for r in resources if r.amount > 0),
                     key=lambda r: np.linalg.norm(self.pos - r.pos), default=None)
        if closest:
            dist = np.linalg.norm(self.pos - closest.pos)
            if dist < self.sight_range * 2:
                attract = (closest.pos - self.pos) * 0.1
                self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
                if dist < 2.0:
                    consumed = min(0.1, closest.amount)
                    self.energy += consumed
                    closest.amount -= consumed

        self.pos = (self.pos + self.vel) % sim.world_size
        return True

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100, 100), db_path=None, n_resources=5):
        super().__init__(db_path=db_path, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, self.world_size, 2))
                        for i in range(n_resources)]

def run_trial(agent_class, n_agents=50, n_steps=100, seed=None, **kwargs):
    if seed:
        np.random.seed(seed)

    sim = WorldSim()
    agents = [agent_class(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                         energy=np.random.uniform(0.5, 1.5), **kwargs)
             for i in range(n_agents)]
    for a in agents:
        sim.add_agent(a, 0)

    alive = agents.copy()
    for _ in range(n_steps):
        alive = [a for a in alive if a.update(sim, alive, sim.resources)]
        for r in sim.resources:
            if r.amount < r.initial_amount / 2:
                r.amount += 0.1
        if not alive:
            break

    return {
        "survivors": len(alive),
        "total_flocks": sum(a.flock_count for a in agents),
        "flocks_per_agent": sum(a.flock_count for a in agents) / n_agents
    }

def main():
    print("CYCLE 376: ADAPTIVE EMERGENCE CONTROL")
    print("=" * 55)
    print()

    PatternMemory().clear_patterns()

    n_trials = 5
    results = {}

    # Test adaptive agents
    print("Testing ADAPTIVE agents...")
    adaptive_trials = [run_trial(AdaptiveAgent, seed=42+t) for t in range(n_trials)]
    results["adaptive"] = {
        "avg_flocks": round(np.mean([t["flocks_per_agent"] for t in adaptive_trials]), 1),
        "avg_survivors": round(np.mean([t["survivors"] for t in adaptive_trials]), 1),
        "std_flocks": round(np.std([t["flocks_per_agent"] for t in adaptive_trials]), 1)
    }
    print(f"  Flocks/agent: {results['adaptive']['avg_flocks']} ± {results['adaptive']['std_flocks']}")
    print(f"  Survivors: {results['adaptive']['avg_survivors']}")

    # Test fixed agents (optimal from C375)
    print("\nTesting FIXED agents (C=0.03)...")
    fixed_trials = [run_trial(FixedAgent, cohesion=0.03, seed=42+t) for t in range(n_trials)]
    results["fixed_optimal"] = {
        "avg_flocks": round(np.mean([t["flocks_per_agent"] for t in fixed_trials]), 1),
        "avg_survivors": round(np.mean([t["survivors"] for t in fixed_trials]), 1),
        "std_flocks": round(np.std([t["flocks_per_agent"] for t in fixed_trials]), 1)
    }
    print(f"  Flocks/agent: {results['fixed_optimal']['avg_flocks']} ± {results['fixed_optimal']['std_flocks']}")
    print(f"  Survivors: {results['fixed_optimal']['avg_survivors']}")

    # Test fixed agents (default)
    print("\nTesting FIXED agents (C=0.05)...")
    default_trials = [run_trial(FixedAgent, cohesion=0.05, seed=42+t) for t in range(n_trials)]
    results["fixed_default"] = {
        "avg_flocks": round(np.mean([t["flocks_per_agent"] for t in default_trials]), 1),
        "avg_survivors": round(np.mean([t["survivors"] for t in default_trials]), 1),
        "std_flocks": round(np.std([t["flocks_per_agent"] for t in default_trials]), 1)
    }
    print(f"  Flocks/agent: {results['fixed_default']['avg_flocks']} ± {results['fixed_default']['std_flocks']}")
    print(f"  Survivors: {results['fixed_default']['avg_survivors']}")

    # Analysis
    print("\n" + "=" * 55)
    print("COMPARISON")
    print("=" * 55)
    print(f"Adaptive:      {results['adaptive']['avg_flocks']} flocks, {results['adaptive']['avg_survivors']} surv")
    print(f"Fixed (0.03):  {results['fixed_optimal']['avg_flocks']} flocks, {results['fixed_optimal']['avg_survivors']} surv")
    print(f"Fixed (0.05):  {results['fixed_default']['avg_flocks']} flocks, {results['fixed_default']['avg_survivors']} surv")

    # Verdict
    if results['adaptive']['avg_flocks'] > results['fixed_optimal']['avg_flocks']:
        print("\n>> ADAPTIVE WINS on flocking")
    else:
        print("\n>> FIXED wins on flocking")

    if results['adaptive']['avg_survivors'] > results['fixed_optimal']['avg_survivors']:
        print(">> ADAPTIVE WINS on survival")
    else:
        print(">> FIXED wins on survival")

    # Save
    output = {"cycle": 376, "results": results}
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c376_adaptive_control.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved.")

if __name__ == "__main__":
    main()
