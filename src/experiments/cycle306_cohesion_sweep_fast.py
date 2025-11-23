"""
CYCLE 306: Fast Cohesion Parameter Sweep
Objective: Map cohesion-emergence relationship without expensive lineage calculations
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from memory.pattern_memory import PatternMemory

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0,
                 metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor

    def update(self, world_size, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False, 0

        # Count neighbors
        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)
        neighbors = 0

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors += 1

        # Cohesion behavior
        if neighbors > 0:
            avg_neighbor_pos /= neighbors
            avg_neighbor_vel /= neighbors
            cohesion_vec = (avg_neighbor_pos - self.pos) * self.cohesion_factor
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vec)
            self.vel = self.vel.clip(-self.move_speed, self.move_speed)

        # Resource seeking
        closest_res = None
        min_dist = float('inf')
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_res = res

        if closest_res and min_dist < self.sight_range * 2:
            attract = (closest_res.pos - self.pos) * 0.1
            self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
            if min_dist < 2.0:
                consumed = min(self.energy * 0.1, closest_res.amount)
                self.energy += consumed
                closest_res.amount -= consumed

        # Move
        self.pos = (self.pos + self.vel) % world_size

        # Return flock size (neighbors + self)
        flock_size = neighbors + 1 if neighbors > 2 else 0
        return True, flock_size

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_sim(cohesion, n_agents=50, steps=100):
    """Run single simulation, return metrics"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion) for i in range(n_agents)]

    flock_sizes = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        for agent in alive:
            survived, flock_size = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                if flock_size > 0:
                    flock_sizes.append(flock_size)
        alive = new_alive
        if not alive: break

        # Regenerate resources
        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    return {
        "agents_survived": len(alive),
        "flock_count": len(flock_sizes),
        "avg_flock_size": round(np.mean(flock_sizes), 2) if flock_sizes else 0,
        "max_flock_size": max(flock_sizes) if flock_sizes else 0
    }

def main():
    print("CYCLE 306: FAST COHESION PARAMETER SWEEP")
    print("=" * 50)

    # Parameter sweep: 10 cohesion values, 5 seeds each
    cohesion_values = np.linspace(0.01, 0.50, 10)
    n_seeds = 5

    results = []

    for cf in cohesion_values:
        seed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 100 + int(cf * 1000))  # Reproducible
            r = run_sim(cf)
            seed_results.append(r)

        # Average across seeds
        avg_result = {
            "cohesion_factor": round(cf, 3),
            "avg_flock_size": round(np.mean([r["avg_flock_size"] for r in seed_results]), 2),
            "avg_flock_count": round(np.mean([r["flock_count"] for r in seed_results]), 0),
            "survival_rate": round(np.mean([r["agents_survived"] for r in seed_results]) / 50 * 100, 1),
            "max_flock_size": max([r["max_flock_size"] for r in seed_results])
        }
        results.append(avg_result)
        print(f"Cohesion {cf:.3f}: AvgSize={avg_result['avg_flock_size']}, "
              f"Count={avg_result['avg_flock_count']}, Survival={avg_result['survival_rate']}%")

    # Analysis
    print("\n" + "=" * 50)
    print("ANALYSIS: Control-Emergence Relationship")
    print("=" * 50)

    # Find optimal cohesion
    best_by_size = max(results, key=lambda x: x["avg_flock_size"])
    best_by_count = max(results, key=lambda x: x["avg_flock_count"])

    print(f"\nLargest flocks at cohesion={best_by_size['cohesion_factor']}: "
          f"size={best_by_size['avg_flock_size']}")
    print(f"Most flocks at cohesion={best_by_count['cohesion_factor']}: "
          f"count={best_by_count['avg_flock_count']}")

    # Calculate correlation
    cfs = [r["cohesion_factor"] for r in results]
    sizes = [r["avg_flock_size"] for r in results]
    counts = [r["avg_flock_count"] for r in results]

    corr_size = np.corrcoef(cfs, sizes)[0, 1]
    corr_count = np.corrcoef(cfs, counts)[0, 1]

    print(f"\nCorrelation (cohesion vs flock_size): {corr_size:.3f}")
    print(f"Correlation (cohesion vs flock_count): {corr_count:.3f}")

    # Save results
    output = {
        "experiment": "C306_cohesion_sweep_fast",
        "parameters": {"n_agents": 50, "steps": 100, "seeds": 5, "cohesion_range": [0.01, 0.50]},
        "results": results,
        "analysis": {
            "best_for_large_flocks": best_by_size,
            "best_for_many_flocks": best_by_count,
            "correlation_size": round(corr_size, 3),
            "correlation_count": round(corr_count, 3)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c306_cohesion_sweep.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c306_cohesion_sweep.json")
    print("\n--- C306 Complete ---")

if __name__ == "__main__":
    main()
