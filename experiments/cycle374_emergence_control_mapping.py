"""
CYCLE 374: Emergence Control Parameter Mapping
Objective: Map the relationship between cohesion factor and emergent flock size.
Builds on C304 initial exploration.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import time
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from memory.pattern_memory import PatternMemory

# Reuse agent classes from C304
class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0,
                 move_speed=1.0, metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor
        self.flock_count = 0

    def update(self, sim, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False

        # Find neighbors
        neighbors = []
        for other in all_agents:
            if other == self:
                continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                neighbors.append(other)

        # Flocking behavior
        if neighbors:
            avg_pos = np.mean([n.pos for n in neighbors], axis=0)
            avg_vel = np.mean([n.vel for n in neighbors], axis=0)

            cohesion = (avg_pos - self.pos) * self.cohesion_factor
            alignment = (avg_vel - self.vel) * 0.1

            self.vel = (self.vel + cohesion + alignment).clip(-self.move_speed, self.move_speed)

            # Track flock formation
            if len(neighbors) > 2:
                self.flock_count += 1

        # Resource seeking
        closest = None
        min_dist = float('inf')
        for res in resources:
            if res.amount > 0:
                d = np.linalg.norm(self.pos - res.pos)
                if d < min_dist:
                    min_dist = d
                    closest = res

        if closest and min_dist < self.sight_range * 2:
            attract = (closest.pos - self.pos) * 0.1
            self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)

            if min_dist < 2.0:
                consumed = min(0.1, closest.amount)
                self.energy += consumed
                closest.amount -= consumed

        # Move
        self.pos += self.vel
        self.pos %= sim.world_size

        return True

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100, 100), db_path=None, n_resources=5):
        super().__init__(db_path=db_path, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [
            Resource(f"Res_{i}", np.random.uniform(0, self.world_size, 2))
            for i in range(n_resources)
        ]

def run_trial(cohesion_factor, n_agents=50, n_steps=100, seed=None):
    """Run a single trial with given cohesion factor."""
    if seed is not None:
        np.random.seed(seed)

    sim = WorldSim(world_size=(100, 100), n_resources=5)

    agents = []
    for i in range(n_agents):
        agent = SwarmAgent(
            f"Agent_{i}",
            np.random.uniform(0, sim.world_size, 2),
            energy=np.random.uniform(0.5, 1.5),
            move_speed=2.0,
            cohesion_factor=cohesion_factor
        )
        agents.append(agent)
        sim.add_agent(agent, 0)

    alive = agents.copy()
    for step in range(n_steps):
        new_alive = [a for a in alive if a.update(sim, alive, sim.resources)]
        alive = new_alive

        # Regenerate resources
        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

        if not alive:
            break

    # Calculate metrics
    total_flocks = sum(a.flock_count for a in agents)
    survivors = len(alive)

    return {
        "cohesion": cohesion_factor,
        "survivors": survivors,
        "total_flocks": total_flocks,
        "flocks_per_agent": total_flocks / n_agents if n_agents > 0 else 0
    }

def main():
    print("CYCLE 374: EMERGENCE CONTROL PARAMETER MAPPING")
    print("=" * 55)
    print()

    # Clear patterns
    memory = PatternMemory()
    memory.clear_patterns()
    memory.clear_relationships()

    # Parameter sweep
    cohesion_values = [0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30]
    n_trials = 3  # Multiple trials per cohesion value

    results = []

    for cohesion in cohesion_values:
        trial_results = []
        print(f"Testing cohesion={cohesion}...", end=" ")

        for trial in range(n_trials):
            result = run_trial(cohesion, seed=42 + trial)
            trial_results.append(result)

        # Average across trials
        avg_flocks = np.mean([r["flocks_per_agent"] for r in trial_results])
        avg_survivors = np.mean([r["survivors"] for r in trial_results])

        print(f"Flocks/agent: {avg_flocks:.1f}, Survivors: {avg_survivors:.1f}")

        results.append({
            "cohesion": cohesion,
            "avg_flocks_per_agent": round(avg_flocks, 2),
            "avg_survivors": round(avg_survivors, 2),
            "trials": trial_results
        })

    # Analysis
    print("\n" + "=" * 55)
    print("CONTROL RESPONSE CURVE")
    print("=" * 55)

    for r in results:
        bar = "█" * int(r["avg_flocks_per_agent"] / 2)
        print(f"Cohesion {r['cohesion']:0.2f}: {bar} {r['avg_flocks_per_agent']:.1f}")

    # Find optimal
    max_flocks = max(results, key=lambda x: x["avg_flocks_per_agent"])
    print(f"\nOptimal cohesion: {max_flocks['cohesion']} ({max_flocks['avg_flocks_per_agent']:.1f} flocks/agent)")

    # Save results
    output = {
        "cycle": 374,
        "parameter_sweep": results,
        "optimal_cohesion": max_flocks["cohesion"],
        "max_flocks_per_agent": max_flocks["avg_flocks_per_agent"]
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c374_emergence_control_mapping.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to experiments/results/c374_emergence_control_mapping.json")

if __name__ == "__main__":
    main()
