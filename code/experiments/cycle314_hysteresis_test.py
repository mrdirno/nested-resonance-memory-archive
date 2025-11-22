"""
CYCLE 314: Hysteresis Test
Objective: Test if phase transition shows memory (path-dependence)
Hypothesis: First-order transitions show hysteresis; second-order don't
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

    def update(self, world_size, all_agents, resources, cohesion):
        self.energy -= self.metabolic_rate
        self.cohesion_factor = cohesion  # Update cohesion externally

        if self.energy <= 0:
            return False, 0

        neighbors = 0
        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors += 1

        if neighbors > 0:
            avg_neighbor_pos /= neighbors
            avg_neighbor_vel /= neighbors
            cohesion_vec = (avg_neighbor_pos - self.pos) * self.cohesion_factor
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vec)
            self.vel = self.vel.clip(-self.move_speed, self.move_speed)

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

        self.pos = (self.pos + self.vel) % world_size
        flock_size = neighbors + 1 if neighbors > 2 else 0
        return True, flock_size

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_sweep(n_agents, cohesion_sequence, steps_per_point=20):
    """Run simulation with changing cohesion, measure flock size at each point"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.8, 1.5), move_speed=2.0)
              for i in range(n_agents)]

    results = []
    alive = agents[:]

    for cohesion in cohesion_sequence:
        # Run for steps_per_point steps at this cohesion
        flock_sizes = []
        for step in range(steps_per_point):
            new_alive = []
            for agent in alive:
                survived, flock_size = agent.update(sim.world_size, alive, sim.resources, cohesion)
                if survived:
                    new_alive.append(agent)
                    if flock_size > 0:
                        flock_sizes.append(flock_size)
            alive = new_alive
            if not alive:
                break

            for res in sim.resources:
                if res.amount < res.initial_amount / 2:
                    res.amount += 0.1

        avg_size = np.mean(flock_sizes) if flock_sizes else 0
        results.append({
            "cohesion": cohesion,
            "avg_flock_size": avg_size,
            "alive": len(alive)
        })

        if not alive:
            break

    return results

def main():
    print("CYCLE 314: HYSTERESIS TEST")
    print("=" * 50)
    print("Testing if phase transition shows memory (path-dependence)")

    n_agents = 50
    n_seeds = 6

    # Sweep up and down across critical region
    cohesion_up = np.linspace(0.05, 0.35, 16)  # Low → High
    cohesion_down = cohesion_up[::-1]  # High → Low

    results_up_all = []
    results_down_all = []

    print("\n--- Forward Sweep (Low → High) ---")
    for seed in range(n_seeds):
        np.random.seed(seed * 1000)
        results = run_sweep(n_agents, cohesion_up)
        results_up_all.append(results)

    print("--- Backward Sweep (High → Low) ---")
    for seed in range(n_seeds):
        np.random.seed(seed * 1000 + 500)
        results = run_sweep(n_agents, cohesion_down)
        results_down_all.append(results)

    # Average across seeds
    up_avg = {}
    for c in cohesion_up:
        sizes = [r["avg_flock_size"] for res in results_up_all
                for r in res if abs(r["cohesion"] - c) < 0.001]
        up_avg[round(c, 3)] = round(np.mean(sizes), 2) if sizes else 0

    down_avg = {}
    for c in cohesion_down:
        sizes = [r["avg_flock_size"] for res in results_down_all
                for r in res if abs(r["cohesion"] - c) < 0.001]
        down_avg[round(c, 3)] = round(np.mean(sizes), 2) if sizes else 0

    # Print comparison
    print("\nCohesion | Forward | Backward | Difference")
    print("-" * 45)
    hysteresis_values = []
    for c in sorted(up_avg.keys()):
        fwd = up_avg.get(c, 0)
        bwd = down_avg.get(c, 0)
        diff = abs(fwd - bwd)
        hysteresis_values.append(diff)
        print(f"  {c:.2f}  |  {fwd:5.1f}  |  {bwd:5.1f}   |  {diff:5.2f}")

    # Analysis
    print("\n" + "=" * 50)
    print("HYSTERESIS ANALYSIS")
    print("=" * 50)

    avg_hysteresis = np.mean(hysteresis_values)
    max_hysteresis = max(hysteresis_values)

    print(f"\nAverage hysteresis: {avg_hysteresis:.3f}")
    print(f"Maximum hysteresis: {max_hysteresis:.3f}")

    # Significant hysteresis indicates first-order transition
    if avg_hysteresis > 2.0:
        print("\n** SIGNIFICANT HYSTERESIS DETECTED **")
        print("   Transition shows memory/path-dependence")
        print("   Consistent with first-order transition")
    elif avg_hysteresis > 0.5:
        print("\nModerate hysteresis detected")
        print("   Some path-dependence present")
    else:
        print("\nNo significant hysteresis")
        print("   Consistent with second-order (continuous) transition")

    # Save results
    output = {
        "experiment": "C314_hysteresis_test",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "steps_per_point": 20,
            "cohesion_range": [0.05, 0.35]
        },
        "forward_sweep": up_avg,
        "backward_sweep": down_avg,
        "analysis": {
            "avg_hysteresis": round(avg_hysteresis, 4),
            "max_hysteresis": round(max_hysteresis, 4),
            "significant_hysteresis": bool(avg_hysteresis > 2.0)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c314_hysteresis.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c314_hysteresis.json")
    print("\n--- C314 Complete ---")

if __name__ == "__main__":
    main()
